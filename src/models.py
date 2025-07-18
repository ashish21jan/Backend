from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoRequest(BaseModel):
    """Request model for video generation"""
    subject: str = Field(..., description="Subject area (e.g., Mathematics, Physics)")
    grade: str = Field(..., description="Grade level (e.g., 10, 12)")
    topic: str = Field(..., description="Specific topic to cover")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    target_duration: int = Field(default=600, description="Target video duration in seconds")
    language: str = Field(default="en", description="Language for the video")
    include_examples: bool = Field(default=True, description="Include worked examples")
    include_practice: bool = Field(default=True, description="Include practice problems")
    voice_style: str = Field(default="professional", description="Voice style for narration")
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "Mathematics",
                "grade": "10",
                "topic": "Quadratic Equations",
                "difficulty_level": "medium",
                "target_duration": 600,
                "language": "en",
                "include_examples": True,
                "include_practice": True,
                "voice_style": "professional"
            }
        }

class VideoResponse(BaseModel):
    """Response model for video generation"""
    job_id: str
    status: VideoStatus
    message: str
    estimated_completion_time: int = Field(description="Estimated completion time in seconds")
    video_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ContentAnalysis(BaseModel):
    """Model for content analysis results"""
    trending_topics: List[str]
    competition_analysis: Dict[str, Any]
    content_gaps: List[str]
    recommended_topics: List[str]
    performance_predictions: Dict[str, float]
    
class ScriptSection(BaseModel):
    """Model for script sections"""
    section_type: str = Field(description="Type of section (intro, main, example, conclusion)")
    title: str
    content: str
    duration: int = Field(description="Duration in seconds")
    visual_cues: List[str] = Field(default_factory=list)
    
class Script(BaseModel):
    """Complete script model"""
    title: str
    total_duration: int
    sections: List[ScriptSection]
    key_concepts: List[str]
    learning_objectives: List[str]

class VideoMetadata(BaseModel):
    """YouTube video metadata"""
    title: str
    description: str
    tags: List[str]
    category_id: int = Field(default=27, description="YouTube category ID")
    thumbnail_url: Optional[str] = None
    language: str = Field(default="en")
    
class QualityMetrics(BaseModel):
    """Quality assessment metrics"""
    educational_accuracy: float = Field(ge=0.0, le=1.0)
    content_clarity: float = Field(ge=0.0, le=1.0)
    engagement_potential: float = Field(ge=0.0, le=1.0)
    technical_quality: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    feedback: List[str] = Field(default_factory=list)

class PerformanceMetrics(BaseModel):
    """Video performance metrics"""
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    watch_time_minutes: float = 0.0
    click_through_rate: float = 0.0
    engagement_rate: float = 0.0
    retention_rate: float = 0.0

class ContentIdea(BaseModel):
    """Content idea model"""
    title: str
    description: str
    estimated_views: int
    difficulty_level: DifficultyLevel
    target_audience: str
    key_concepts: List[str]
    estimated_production_time: int = Field(description="Estimated production time in minutes")
    priority_score: float = Field(ge=0.0, le=1.0)

class TrendAnalysis(BaseModel):
    """Trend analysis model"""
    subject: str
    grade: str
    trending_keywords: List[str]
    search_volume_data: Dict[str, int]
    competition_level: str
    content_opportunities: List[ContentIdea]
    market_insights: Dict[str, Any]