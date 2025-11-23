from sqlalchemy.orm import Session
from typing import List, Set, Dict, Any
from .models import RecommendationRequest, RecommendedProduct, RecommendationResponse, Product
from .vector_store import ProductVectorStore
from .orm_models import RecommendationLogORM

def build_blueprint(req: RecommendationRequest) -> List[dict]:
    """
    Convert request into 'blueprint' of constructs with priorities.
    """
    blueprint: List[dict] = []

    for c in req.must_have_constructs:
        blueprint.append({"construct": c, "priority": "must"})

    # Best-practice defaults
    if req.use_case == "selection" and "cognitive_ability" not in req.must_have_constructs:
        blueprint.append({"construct": "cognitive_ability", "priority": "should"})

    if (req.volume == "high" or req.job_family in ["customer_service", "retail"]) \
            and "behavioral_fit" not in req.must_have_constructs:
        blueprint.append({"construct": "behavioral_fit", "priority": "should"})

    if (req.job_level in ["manager", "executive"] or req.use_case == "development") \
            and "personality" not in req.must_have_constructs:
        blueprint.append({"construct": "personality", "priority": "should"})

    for c in req.nice_to_have_constructs:
        blueprint.append({"construct": c, "priority": "nice"})

    seen = set()
    unique_blueprint: List[dict] = []
    for item in blueprint:
        if item["construct"] not in seen:
            seen.add(item["construct"])
            unique_blueprint.append(item)

    return unique_blueprint


def rank_candidates(
    candidates: List[Product],
    construct: str,
    req: RecommendationRequest,
    semantic_scores: Dict[str, float],
) -> List[Product]:
    """
    Rank candidate products using a simple scoring heuristic + semantic similarity from FAISS.
    """
    scored = []

    for p in candidates:
        score = 0.0

        # Construct match
        if construct in p.constructs:
            score += 5.0

        # Job level / family alignment
        if req.job_level in p.job_levels:
            score += 3.0

        if req.job_family in p.job_families:
            score += 3.0

        # Use case match
        if req.use_case in p.use_cases:
            score += 2.0

        # Language compatibility
        if any(lang in p.languages for lang in req.languages):
            score += 2.0

        # Volume suitability
        if req.volume == "high" and "high_volume" in p.tags:
            score += 2.0

        # Duration check
        if p.max_duration_min <= req.max_total_duration_min:
            score += 1.0

        # Semantic similarity from FAISS
        sem = semantic_scores.get(p.product_id, 0.0)
        score += 4.0 * sem  # weight semantic similarity

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for score, p in scored if score > 0]


def match_products(
    blueprint: List[dict],
    req: RecommendationRequest,
    products: List[Product],
    vector_store: ProductVectorStore,
) -> List[RecommendedProduct]:
    """
    Use blueprint + FAISS semantic search to pick best products per construct.
    """
    recommendations: List[RecommendedProduct] = []

    # Get semantic similarity of all products against the job description
    sem_results = vector_store.search(
        f"{req.job_title}. {req.job_description}",
        top_k=len(products)
    )
    semantic_scores = {p.product_id: score for p, score in sem_results}

    for element in blueprint:
        construct = element["construct"]

        # Filter catalogue by construct & language
        candidates = [
            p for p in products
            if construct in p.constructs
            and any(lang in p.languages for lang in req.languages)
        ]

        ranked = rank_candidates(candidates, construct, req, semantic_scores)

        if ranked:
            p = ranked[0]
            reason = (
                f"Best match for construct '{construct}' "
                f"for {req.job_family}/{req.job_level} ({req.use_case}); "
                f"semantic_fit={semantic_scores.get(p.product_id, 0.0):.2f}."
            )
            recommendations.append(
                RecommendedProduct(
                    product_id=p.product_id,
                    name=p.name,
                    reason=reason,
                    max_duration_min=p.max_duration_min,
                )
            )

    return recommendations


def build_bundle(
    recs: List[RecommendedProduct],
    req: RecommendationRequest,
    products: List[Product],
) -> RecommendationResponse:
    """
    Compose bundle while respecting time limit.
    """
    chosen: List[RecommendedProduct] = []
    total_duration = 0
    constructs_covered: Set[str] = set()

    for r in recs:
        if total_duration + r.max_duration_min <= req.max_total_duration_min:
            chosen.append(r)
            total_duration += r.max_duration_min

            prod = next((p for p in products if p.product_id == r.product_id), None)
            if prod:
                constructs_covered.update(prod.constructs)

    debug: Dict[str, Any] = {
        "requested_job_family": req.job_family,
        "requested_job_level": req.job_level,
        "use_case": req.use_case,
    }

    return RecommendationResponse(
        bundle_id="AUTO_BUNDLE_V1",
        products=chosen,
        total_duration_min=total_duration,
        constructs_covered=sorted(list(constructs_covered)),
        debug=debug,
    )



def log_recommendation(
    db: Session,
    req: RecommendationRequest,
    resp: RecommendationResponse
):
    log = RecommendationLogORM(
        job_title=req.job_title,
        job_family=req.job_family,
        job_level=req.job_level,
        use_case=req.use_case,
        volume=req.volume,
        bundle_id=resp.bundle_id,
        total_duration_min=resp.total_duration_min,
        constructs_covered=resp.constructs_covered,
        request_json=req.dict(),
        products_json=[p.dict() for p in resp.products],
    )
    db.add(log)
    db.commit()
