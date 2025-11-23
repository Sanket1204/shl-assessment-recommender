from pydantic import BaseModel
from typing import List, Literal, Optional
from .orm_models import ProductORM


class Product(BaseModel):
    product_id: str
    name: str
    description: str
    category: str
    constructs: List[str]
    use_cases: List[str]
    job_levels: List[str]
    job_families: List[str]
    max_duration_min: int
    languages: List[str]
    tags: List[str] = []

    @staticmethod
    def from_orm_model(o: ProductORM) -> "Product":
        return Product(
            product_id=o.product_id,
            name=o.name,
            description=o.description,
            category=o.category,
            constructs=o.constructs,
            use_cases=o.use_cases,
            job_levels=o.job_levels,
            job_families=o.job_families,
            max_duration_min=o.max_duration_min,
            languages=o.languages,
            tags=o.tags or [],
        )


class RecommendationRequest(BaseModel):
    job_title: str
    job_description: str = ""
    job_family: str
    job_level: Literal["entry", "junior", "graduate", "professional", "manager", "executive"]
    use_case: Literal["selection", "development", "succession"]
    volume: Literal["low", "medium", "high"]
    assessment_budget: Literal["low", "medium", "high"]
    max_total_duration_min: int
    must_have_constructs: List[str] = []
    nice_to_have_constructs: List[str] = []
    languages: List[str] = ["en"]
    unsupervised_ok: bool = True


class RecommendedProduct(BaseModel):
    product_id: str
    name: str
    reason: str
    max_duration_min: int


class RecommendationResponse(BaseModel):
    bundle_id: str
    products: List[RecommendedProduct]
    total_duration_min: int
    constructs_covered: List[str]
    debug: Optional[dict] = None
 