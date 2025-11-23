from sqlalchemy.orm import Session
from .orm_models import ProductORM


def seed_products_if_empty(db: Session):
    count = db.query(ProductORM).count()
    if count > 0:
        return

    mock_products = [
        ProductORM(
            product_id="VERIFY_G_PLUS",
            name="SHL Verify G+ General Ability",
            description="General cognitive ability combining numerical, inductive, deductive reasoning.",
            category="A_ABILITY",
            constructs=["cognitive_ability", "numerical_reasoning", "inductive_reasoning"],
            use_cases=["selection"],
            job_levels=["graduate", "professional", "manager"],
            job_families=["customer_service", "sales", "it", "analytics", "operations"],
            max_duration_min=36,
            languages=["en", "fr"],
            tags=["mobile_friendly", "unsupervised_ok"],
        ),
        ProductORM(
            product_id="SJT_CUSTOMER_SERVICE",
            name="Customer Service Situational Judgement Test",
            description="SJT for customer service and retail roles.",
            category="B_SJT",
            constructs=["behavioral_fit", "situational_judgement"],
            use_cases=["selection"],
            job_levels=["entry", "junior"],
            job_families=["customer_service", "retail"],
            max_duration_min=25,
            languages=["en"],
            tags=["high_volume"],
        ),
        ProductORM(
            product_id="OPQ32R",
            name="Occupational Personality Questionnaire (OPQ32r)",
            description="Comprehensive workplace personality questionnaire.",
            category="P_PERSONALITY",
            constructs=["personality"],
            use_cases=["selection", "development", "succession"],
            job_levels=["graduate", "professional", "manager", "executive"],
            job_families=["sales", "customer_service", "leadership", "it", "operations"],
            max_duration_min=30,
            languages=["en", "fr", "de", "es"],
            tags=["broad_personality"],
        ),
        ProductORM(
            product_id="MQ_MOTIVATION",
            name="Motivation Questionnaire (MQ)",
            description="Measures key drivers and motivators at work.",
            category="M_MOTIVATION",
            constructs=["motivation"],
            use_cases=["development", "succession"],
            job_levels=["professional", "manager", "executive"],
            job_families=["leadership", "sales", "it", "operations"],
            max_duration_min=20,
            languages=["en"],
            tags=["development_focus"],
        ),
    ]

    db.add_all(mock_products)
    db.commit()
