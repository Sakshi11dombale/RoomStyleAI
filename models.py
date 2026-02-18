# models.py - SQLAlchemy models for recording uploads and predictions
from sqlalchemy import Column, Integer, String, LargeBinary, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()


class UploadRecord(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    raw_bytes = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    predictions = relationship("PredictionRecord", back_populates="upload")


class PredictionRecord(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"))
    predicted_style = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    dominant_colors = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    upload = relationship("UploadRecord", back_populates="predictions")

