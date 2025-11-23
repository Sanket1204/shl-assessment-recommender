from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .db import get_db, Base, engine
from .orm_models import ProductORM, RecommendationLogORM
from .models import RecommendationRequest, RecommendationResponse, Product
from .catalogue import seed_products_if_empty
from .vector_store import ProductVectorStore
from .recommender import build_blueprint, match_products, build_bundle, log_recommendation
from .pdf_utils import build_recommendation_pdf

# Create tables at startup (safe): attempt to create tables but do not crash on import

app = FastAPI(
    title="SHL Assessment Recommendation Engine",
    version="0.2.0",
    description="FastAPI + FAISS + Postgres backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory vector store (rebuilt on startup)
vector_store: ProductVectorStore | None = None


@app.on_event("startup")
def startup_event():
    global vector_store
    # ensure DB is reachable and create tables if possible
    try:
        conn = engine.connect()
        conn.close()
        Base.metadata.create_all(bind=engine)
    except Exception:
        # DB not available (e.g. running locally without Postgres). Don't crash here;
        # operations that require the DB will fail later with clearer errors.
        print("Warning: could not connect to database at startup; continuing without creating tables.")
    # use a real Session for seeding + reading
    from .db import SessionLocal
    s = SessionLocal()
    try:
        seed_products_if_empty(s)
        products_orm = s.query(ProductORM).all()
        products = [Product.from_orm_model(o) for o in products_orm]
        vector_store = ProductVectorStore(products)
    finally:
        s.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest, db: Session = Depends(get_db)):
    global vector_store
    if vector_store is None:
        # rebuild if needed
        products_orm = db.query(ProductORM).all()
        products = [Product.from_orm_model(o) for o in products_orm]
        vector_store = ProductVectorStore(products)

    products_orm = db.query(ProductORM).all()
    products = [Product.from_orm_model(o) for o in products_orm]

    blueprint = build_blueprint(req)
    recs = match_products(blueprint, req, products, vector_store)
    resp = build_bundle(recs, req, products)

    log_recommendation(db, req, resp)
    return resp


@app.post("/recommend/pdf")
def recommend_pdf(req: RecommendationRequest, db: Session = Depends(get_db)):
    resp: RecommendationResponse = recommend(req, db)  # reuse logic
    pdf_buffer = build_recommendation_pdf(req, resp)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="recommendation.pdf"'},
    )


# --- Simple admin: list products & logs (no auth for now) ---

@app.get("/admin/products", response_model=list[Product])
def list_products(db: Session = Depends(get_db)):
    products_orm = db.query(ProductORM).all()
    return [Product.from_orm_model(o) for o in products_orm]


@app.get("/admin/analytics")
def analytics(db: Session = Depends(get_db)):
    total = db.query(RecommendationLogORM).count()
    by_family = (
        db.query(RecommendationLogORM.job_family, func.count(RecommendationLogORM.id))
        .group_by(RecommendationLogORM.job_family)
        .all()
    )
    return {
        "total_requests": total,
        "by_job_family": {k: v for k, v in by_family},
    }
