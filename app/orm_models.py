from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy import Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from typing import List
from .db import Base


class ProductORM(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    constructs = Column(JSON, nullable=False)
    use_cases = Column(JSON, nullable=False)
    job_levels = Column(JSON, nullable=False)
    job_families = Column(JSON, nullable=False)
    max_duration_min = Column(Integer, nullable=False)
    languages = Column(JSON, nullable=False)
    tags = Column(JSON, nullable=True)


class RecommendationLogORM(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    job_title = Column(String(255))
    job_family = Column(String(100))
    job_level = Column(String(50))
    use_case = Column(String(50))
    volume = Column(String(50))
    bundle_id = Column(String(50))
    total_duration_min = Column(Integer)
    constructs_covered = Column(JSON)
    request_json = Column(JSON)
    products_json = Column(JSON)
