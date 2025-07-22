"""Pydantic models for API requests and responses."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str


class Timestamp(BaseModel):
    """Timestamp model for video navigation."""
    start: float
    end: float
    text: str


class QuestionResponse(BaseModel):
    """Response model for question answers."""
    answer: str
    timestamps: List[Timestamp] = []
    confidence: float = 1.0


class VideoProcessResponse(BaseModel):
    """Response model for video processing."""
    status: str
    message: str
    transcript_length: int