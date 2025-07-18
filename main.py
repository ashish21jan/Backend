from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Import our modules
from src.content_intelligence import ContentIntelligence
from src.video_generator import VideoGenerator
from src.quality_assurance import QualityAssurance
from src.performance_optimizer import PerformanceOptimizer
from src.database import Database
from src.models import VideoRequest, VideoResponse, ContentAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Content Automation Engine",
    description="End-to-end automation for educational video content creation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = Database()
content_intelligence = ContentIntelligence()
video_generator = VideoGenerator()
quality_assurance = QualityAssurance()
performance_optimizer = PerformanceOptimizer()

@app.on_event("startup")
async def startup_event():
    """Initialize database and components on startup"""
    await db.init_db()
    logger.info("YouTube Content Automation Engine started successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "YouTube Content Automation Engine",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check with component status"""
    return {
        "status": "healthy",
        "components": {
            "database": "connected",
            "content_intelligence": "ready",
            "video_generator": "ready",
            "quality_assurance": "ready",
            "performance_optimizer": "ready"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze-trends")
async def analyze_trends(subject: str = "mathematics", grade: str = "10"):
    """Analyze trending topics and content opportunities"""
    try:
        analysis = await content_intelligence.analyze_trends(subject, grade)
        return {
            "status": "success",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-content-ideas")
async def generate_content_ideas(
    subject: str,
    grade: str,
    topic: str,
    difficulty_level: str = "medium"
):
    """Generate content ideas based on subject and topic"""
    try:
        ideas = await content_intelligence.generate_content_ideas(
            subject, grade, topic, difficulty_level
        )
        return {
            "status": "success",
            "ideas": ideas,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating content ideas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-video", response_model=VideoResponse)
async def create_video(
    video_request: VideoRequest,
    background_tasks: BackgroundTasks
):
    """Create a complete educational video from topic specification"""
    try:
        # Start video generation process
        job_id = await video_generator.start_video_generation(video_request)
        
        # Add background task for processing
        background_tasks.add_task(
            process_video_generation,
            job_id,
            video_request
        )
        
        return VideoResponse(
            job_id=job_id,
            status="processing",
            message="Video generation started",
            estimated_completion_time=1800  # 30 minutes
        )
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video-status/{job_id}")
async def get_video_status(job_id: str):
    """Get the status of a video generation job"""
    try:
        status = await video_generator.get_job_status(job_id)
        return {
            "job_id": job_id,
            "status": status["status"],
            "progress": status.get("progress", 0),
            "message": status.get("message", ""),
            "video_url": status.get("video_url"),
            "metadata": status.get("metadata"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting video status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-performance")
async def optimize_performance(video_id: str, target_metrics: Dict[str, Any]):
    """Optimize video performance based on target metrics"""
    try:
        optimization = await performance_optimizer.optimize_video(
            video_id, target_metrics
        )
        return {
            "status": "success",
            "optimization": optimization,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error optimizing performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        dashboard_data = await performance_optimizer.get_dashboard_data()
        return {
            "status": "success",
            "data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content-library")
async def get_content_library(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    status: Optional[str] = None
):
    """Get content library with filtering options"""
    try:
        content = await db.get_content_library(subject, grade, status)
        return {
            "status": "success",
            "content": content,
            "total_count": len(content),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting content library: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_generation(job_id: str, video_request: VideoRequest):
    """Background task to process video generation"""
    try:
        # Update job status
        await video_generator.update_job_status(job_id, "processing", 10)
        
        # Generate script
        script = await video_generator.generate_script(video_request)
        await video_generator.update_job_status(job_id, "processing", 30)
        
        # Quality check for script
        script_quality = await quality_assurance.validate_script(script)
        if script_quality["score"] < 0.7:
            await video_generator.update_job_status(
                job_id, "failed", 30, "Script quality below threshold"
            )
            return
        
        # Generate voiceover
        audio_path = await video_generator.generate_voiceover(script)
        await video_generator.update_job_status(job_id, "processing", 50)
        
        # Generate visuals
        visuals = await video_generator.generate_visuals(video_request, script)
        await video_generator.update_job_status(job_id, "processing", 70)
        
        # Assemble video
        video_path = await video_generator.assemble_video(
            script, audio_path, visuals
        )
        await video_generator.update_job_status(job_id, "processing", 85)
        
        # Generate metadata
        metadata = await video_generator.generate_metadata(video_request, script)
        await video_generator.update_job_status(job_id, "processing", 95)
        
        # Final quality check
        final_quality = await quality_assurance.validate_video(video_path)
        if final_quality["score"] < 0.8:
            await video_generator.update_job_status(
                job_id, "failed", 95, "Final video quality below threshold"
            )
            return
        
        # Complete job
        await video_generator.update_job_status(
            job_id, "completed", 100, "Video generation completed successfully",
            video_url=video_path, metadata=metadata
        )
        
        logger.info(f"Video generation completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in video generation job {job_id}: {str(e)}")
        await video_generator.update_job_status(
            job_id, "failed", 0, str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)