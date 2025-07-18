import asyncio
import json
import logging
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta
import openai
from googleapiclient.discovery import build
import os
from .models import TrendAnalysis, ContentIdea, DifficultyLevel

logger = logging.getLogger(__name__)

class ContentIntelligence:
    """Content Intelligence Engine for analyzing trends and generating content ideas"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key) if self.youtube_api_key else None
        
    async def analyze_trends(self, subject: str, grade: str) -> TrendAnalysis:
        """Analyze trending topics and content opportunities"""
        try:
            # Fetch trending keywords
            trending_keywords = await self._get_trending_keywords(subject, grade)
            
            # Analyze competition
            competition_data = await self._analyze_competition(subject, grade)
            
            # Generate content opportunities
            content_opportunities = await self._generate_content_opportunities(
                subject, grade, trending_keywords
            )
            
            # Get search volume data (simulated for demo)
            search_volume_data = await self._get_search_volume_data(trending_keywords)
            
            return TrendAnalysis(
                subject=subject,
                grade=grade,
                trending_keywords=trending_keywords,
                search_volume_data=search_volume_data,
                competition_level=competition_data.get("level", "medium"),
                content_opportunities=content_opportunities,
                market_insights=competition_data
            )
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            raise
    
    async def generate_content_ideas(
        self, 
        subject: str, 
        grade: str, 
        topic: str, 
        difficulty_level: str
    ) -> List[ContentIdea]:
        """Generate content ideas for a specific topic"""
        try:
            prompt = f"""
            Generate 5 high-quality educational video content ideas for:
            - Subject: {subject}
            - Grade: {grade}
            - Topic: {topic}
            - Difficulty: {difficulty_level}
            
            For each idea, provide:
            1. Engaging title (YouTube optimized)
            2. Detailed description
            3. Key concepts to cover
            4. Target audience specifics
            5. Estimated view potential
            6. Production time estimate
            
            Focus on content that would perform well on YouTube for educational channels.
            Consider current trends and student needs.
            
            Return as JSON array with the following structure:
            [
                {
                    "title": "...",
                    "description": "...",
                    "key_concepts": ["...", "..."],
                    "target_audience": "...",
                    "estimated_views": 50000,
                    "estimated_production_time": 120,
                    "priority_score": 0.85
                }
            ]
            """
            
            response = await self._call_openai(prompt)
            ideas_data = json.loads(response)
            
            content_ideas = []
            for idea in ideas_data:
                content_ideas.append(ContentIdea(
                    title=idea["title"],
                    description=idea["description"],
                    estimated_views=idea["estimated_views"],
                    difficulty_level=DifficultyLevel(difficulty_level),
                    target_audience=idea["target_audience"],
                    key_concepts=idea["key_concepts"],
                    estimated_production_time=idea["estimated_production_time"],
                    priority_score=idea["priority_score"]
                ))
            
            return content_ideas
            
        except Exception as e:
            logger.error(f"Error generating content ideas: {str(e)}")
            raise
    
    async def _get_trending_keywords(self, subject: str, grade: str) -> List[str]:
        """Get trending keywords for the subject and grade"""
        try:
            # In a real implementation, this would use Google Trends API
            # For demo purposes, we'll use AI to generate relevant keywords
            prompt = f"""
            Generate 10 trending keywords for {subject} Grade {grade} educational content.
            Focus on topics that students are currently searching for and would perform well on YouTube.
            Return as a simple JSON array of strings.
            """
            
            response = await self._call_openai(prompt)
            keywords = json.loads(response)
            return keywords[:10]  # Limit to 10 keywords
            
        except Exception as e:
            logger.error(f"Error getting trending keywords: {str(e)}")
            # Return fallback keywords
            return [f"{subject} {grade}", f"{subject} basics", f"{subject} problems"]
    
    async def _analyze_competition(self, subject: str, grade: str) -> Dict[str, Any]:
        """Analyze competition in the educational content space"""
        try:
            if not self.youtube:
                return {"level": "medium", "top_channels": [], "avg_views": 10000}
            
            # Search for competing content
            search_query = f"{subject} grade {grade} education"
            search_response = self.youtube.search().list(
                q=search_query,
                part='snippet',
                type='video',
                maxResults=25,
                order='viewCount'
            ).execute()
            
            videos = search_response.get('items', [])
            
            # Analyze the results
            total_views = 0
            channels = set()
            
            for video in videos:
                video_id = video['id']['videoId']
                video_stats = self.youtube.videos().list(
                    part='statistics',
                    id=video_id
                ).execute()
                
                if video_stats['items']:
                    views = int(video_stats['items'][0]['statistics'].get('viewCount', 0))
                    total_views += views
                    channels.add(video['snippet']['channelTitle'])
            
            avg_views = total_views / len(videos) if videos else 0
            
            # Determine competition level
            if avg_views > 100000:
                competition_level = "high"
            elif avg_views > 10000:
                competition_level = "medium"
            else:
                competition_level = "low"
            
            return {
                "level": competition_level,
                "top_channels": list(channels)[:5],
                "avg_views": avg_views,
                "total_videos_analyzed": len(videos)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competition: {str(e)}")
            return {"level": "medium", "top_channels": [], "avg_views": 10000}
    
    async def _generate_content_opportunities(
        self, 
        subject: str, 
        grade: str, 
        trending_keywords: List[str]
    ) -> List[ContentIdea]:
        """Generate content opportunities based on trends"""
        try:
            keywords_str = ", ".join(trending_keywords)
            prompt = f"""
            Based on these trending keywords for {subject} Grade {grade}: {keywords_str}
            
            Generate 3 high-opportunity content ideas that:
            1. Address trending topics
            2. Have low competition
            3. High student demand
            4. Good YouTube performance potential
            
            Return as JSON array with ContentIdea structure.
            """
            
            response = await self._call_openai(prompt)
            ideas_data = json.loads(response)
            
            opportunities = []
            for idea in ideas_data:
                opportunities.append(ContentIdea(
                    title=idea["title"],
                    description=idea["description"],
                    estimated_views=idea.get("estimated_views", 25000),
                    difficulty_level=DifficultyLevel(idea.get("difficulty_level", "medium")),
                    target_audience=idea.get("target_audience", f"Grade {grade} students"),
                    key_concepts=idea.get("key_concepts", []),
                    estimated_production_time=idea.get("estimated_production_time", 90),
                    priority_score=idea.get("priority_score", 0.7)
                ))
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error generating content opportunities: {str(e)}")
            return []
    
    async def _get_search_volume_data(self, keywords: List[str]) -> Dict[str, int]:
        """Get search volume data for keywords (simulated)"""
        # In a real implementation, this would use Google Keyword Planner API
        # For demo purposes, we'll simulate search volumes
        search_volumes = {}
        for keyword in keywords:
            # Simulate search volume based on keyword length and common terms
            base_volume = 5000
            if "math" in keyword.lower():
                base_volume *= 2
            if "class" in keyword.lower() or "grade" in keyword.lower():
                base_volume *= 1.5
            
            # Add some randomness
            import random
            volume = int(base_volume * (0.5 + random.random()))
            search_volumes[keyword] = volume
        
        return search_volumes
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with error handling"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content strategist specializing in YouTube optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise