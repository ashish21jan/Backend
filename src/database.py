import asyncio
import logging
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class Database:
    """Database management for content automation system"""
    
    def __init__(self):
        self.db_path = os.getenv("DATABASE_URL", "sqlite:///./content_automation.db").replace("sqlite:///", "")
        self.connection = None
        
    async def init_db(self):
        """Initialize database with required tables"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        try:
            cursor = self.connection.cursor()
            
            # Videos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    difficulty_level TEXT NOT NULL,
                    script_content TEXT,
                    metadata TEXT,
                    file_path TEXT,
                    status TEXT DEFAULT 'pending',
                    quality_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    view_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    share_count INTEGER DEFAULT 0,
                    watch_time_minutes REAL DEFAULT 0.0,
                    click_through_rate REAL DEFAULT 0.0,
                    engagement_rate REAL DEFAULT 0.0,
                    retention_rate REAL DEFAULT 0.0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos (video_id)
                )
            """)
            
            # Content ideas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    subject TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    topic TEXT,
                    difficulty_level TEXT,
                    estimated_views INTEGER,
                    priority_score REAL,
                    key_concepts TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Trending topics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    search_volume INTEGER,
                    competition_level TEXT,
                    trend_score REAL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Quality assessments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    educational_accuracy REAL,
                    content_clarity REAL,
                    engagement_potential REAL,
                    technical_quality REAL,
                    overall_score REAL,
                    feedback TEXT,
                    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos (video_id)
                )
            """)
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    async def save_video(self, video_data: Dict[str, Any]) -> str:
        """Save video information to database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO videos (
                    video_id, title, subject, grade, topic, difficulty_level,
                    script_content, metadata, file_path, status, quality_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_data.get("video_id"),
                video_data.get("title"),
                video_data.get("subject"),
                video_data.get("grade"),
                video_data.get("topic"),
                video_data.get("difficulty_level"),
                json.dumps(video_data.get("script_content", {})),
                json.dumps(video_data.get("metadata", {})),
                video_data.get("file_path"),
                video_data.get("status", "pending"),
                video_data.get("quality_score", 0.0)
            ))
            
            self.connection.commit()
            logger.info(f"Saved video: {video_data.get('video_id')}")
            return video_data.get("video_id")
            
        except Exception as e:
            logger.error(f"Error saving video: {str(e)}")
            raise
    
    async def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video information by ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting video: {str(e)}")
            return None
    
    async def update_video_status(self, video_id: str, status: str, file_path: Optional[str] = None):
        """Update video status"""
        try:
            cursor = self.connection.cursor()
            
            if file_path:
                cursor.execute("""
                    UPDATE videos 
                    SET status = ?, file_path = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE video_id = ?
                """, (status, file_path, video_id))
            else:
                cursor.execute("""
                    UPDATE videos 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE video_id = ?
                """, (status, video_id))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error updating video status: {str(e)}")
            raise
    
    async def save_performance_metrics(self, video_id: str, metrics: Dict[str, Any]):
        """Save performance metrics for a video"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics (
                    video_id, view_count, like_count, comment_count, share_count,
                    watch_time_minutes, click_through_rate, engagement_rate, retention_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_id,
                metrics.get("view_count", 0),
                metrics.get("like_count", 0),
                metrics.get("comment_count", 0),
                metrics.get("share_count", 0),
                metrics.get("watch_time_minutes", 0.0),
                metrics.get("click_through_rate", 0.0),
                metrics.get("engagement_rate", 0.0),
                metrics.get("retention_rate", 0.0)
            ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error saving performance metrics: {str(e)}")
            raise
    
    async def get_performance_metrics(self, video_id: str) -> List[Dict[str, Any]]:
        """Get performance metrics for a video"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM performance_metrics 
                WHERE video_id = ? 
                ORDER BY recorded_at DESC
            """, (video_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return []
    
    async def save_content_idea(self, idea_data: Dict[str, Any]) -> int:
        """Save content idea to database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO content_ideas (
                    title, description, subject, grade, topic, difficulty_level,
                    estimated_views, priority_score, key_concepts, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                idea_data.get("title"),
                idea_data.get("description"),
                idea_data.get("subject"),
                idea_data.get("grade"),
                idea_data.get("topic"),
                idea_data.get("difficulty_level"),
                idea_data.get("estimated_views", 0),
                idea_data.get("priority_score", 0.0),
                json.dumps(idea_data.get("key_concepts", [])),
                idea_data.get("status", "pending")
            ))
            
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving content idea: {str(e)}")
            raise
    
    async def get_content_ideas(
        self, 
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get content ideas with optional filtering"""
        try:
            cursor = self.connection.cursor()
            
            query = "SELECT * FROM content_ideas WHERE 1=1"
            params = []
            
            if subject:
                query += " AND subject = ?"
                params.append(subject)
            
            if grade:
                query += " AND grade = ?"
                params.append(grade)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY priority_score DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting content ideas: {str(e)}")
            return []
    
    async def save_trending_topics(self, topics_data: List[Dict[str, Any]]):
        """Save trending topics to database"""
        try:
            cursor = self.connection.cursor()
            
            for topic in topics_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO trending_topics (
                        keyword, subject, search_volume, competition_level, trend_score
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    topic.get("keyword"),
                    topic.get("subject"),
                    topic.get("search_volume", 0),
                    topic.get("competition_level", "medium"),
                    topic.get("trend_score", 0.0)
                ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error saving trending topics: {str(e)}")
            raise
    
    async def get_trending_topics(self, subject: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending topics"""
        try:
            cursor = self.connection.cursor()
            
            if subject:
                cursor.execute("""
                    SELECT * FROM trending_topics 
                    WHERE subject = ? 
                    ORDER BY trend_score DESC, search_volume DESC 
                    LIMIT ?
                """, (subject, limit))
            else:
                cursor.execute("""
                    SELECT * FROM trending_topics 
                    ORDER BY trend_score DESC, search_volume DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
            return []
    
    async def save_quality_assessment(self, video_id: str, assessment: Dict[str, Any]):
        """Save quality assessment for a video"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO quality_assessments (
                    video_id, educational_accuracy, content_clarity, engagement_potential,
                    technical_quality, overall_score, feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                video_id,
                assessment.get("educational_accuracy", 0.0),
                assessment.get("content_clarity", 0.0),
                assessment.get("engagement_potential", 0.0),
                assessment.get("technical_quality", 0.0),
                assessment.get("overall_score", 0.0),
                json.dumps(assessment.get("feedback", []))
            ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error saving quality assessment: {str(e)}")
            raise
    
    async def get_content_library(
        self, 
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get content library with filtering options"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                SELECT v.*, qa.overall_score, pm.view_count, pm.engagement_rate
                FROM videos v
                LEFT JOIN quality_assessments qa ON v.video_id = qa.video_id
                LEFT JOIN (
                    SELECT video_id, view_count, engagement_rate,
                           ROW_NUMBER() OVER (PARTITION BY video_id ORDER BY recorded_at DESC) as rn
                    FROM performance_metrics
                ) pm ON v.video_id = pm.video_id AND pm.rn = 1
                WHERE 1=1
            """
            params = []
            
            if subject:
                query += " AND v.subject = ?"
                params.append(subject)
            
            if grade:
                query += " AND v.grade = ?"
                params.append(grade)
            
            if status:
                query += " AND v.status = ?"
                params.append(status)
            
            query += " ORDER BY v.updated_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting content library: {str(e)}")
            return []
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for dashboard"""
        try:
            cursor = self.connection.cursor()
            
            # Get total videos
            cursor.execute("SELECT COUNT(*) as total_videos FROM videos")
            total_videos = cursor.fetchone()["total_videos"]
            
            # Get videos by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM videos 
                GROUP BY status
            """)
            status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
            
            # Get average quality score
            cursor.execute("""
                SELECT AVG(overall_score) as avg_quality 
                FROM quality_assessments
            """)
            avg_quality = cursor.fetchone()["avg_quality"] or 0.0
            
            # Get total views
            cursor.execute("""
                SELECT SUM(view_count) as total_views 
                FROM performance_metrics pm
                INNER JOIN (
                    SELECT video_id, MAX(recorded_at) as latest
                    FROM performance_metrics
                    GROUP BY video_id
                ) latest ON pm.video_id = latest.video_id AND pm.recorded_at = latest.latest
            """)
            total_views = cursor.fetchone()["total_views"] or 0
            
            return {
                "total_videos": total_videos,
                "status_counts": status_counts,
                "avg_quality_score": avg_quality,
                "total_views": total_views
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()