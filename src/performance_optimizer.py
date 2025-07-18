import asyncio
import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import openai
from googleapiclient.discovery import build
from .models import PerformanceMetrics, VideoMetadata
from .database import Database

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance Optimization Engine for YouTube content"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key) if self.youtube_api_key else None
        self.db = Database()
        
    async def optimize_video(self, video_id: str, target_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize video performance based on target metrics"""
        try:
            # Get current video performance
            current_metrics = await self._get_video_metrics(video_id)
            
            # Analyze performance gaps
            optimization_plan = await self._analyze_performance_gaps(
                current_metrics, target_metrics
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                video_id, current_metrics, target_metrics
            )
            
            # Create A/B test variants if needed
            ab_tests = await self._create_ab_test_variants(video_id, recommendations)
            
            return {
                "video_id": video_id,
                "current_metrics": current_metrics,
                "target_metrics": target_metrics,
                "optimization_plan": optimization_plan,
                "recommendations": recommendations,
                "ab_tests": ab_tests,
                "estimated_improvement": await self._estimate_improvement(
                    current_metrics, recommendations
                )
            }
            
        except Exception as e:
            logger.error(f"Error optimizing video performance: {str(e)}")
            raise
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data"""
        try:
            # Get recent video performance
            recent_videos = await self._get_recent_video_performance()
            
            # Calculate aggregate metrics
            aggregate_metrics = await self._calculate_aggregate_metrics(recent_videos)
            
            # Get trending topics
            trending_topics = await self._get_trending_topics()
            
            # Get performance insights
            insights = await self._generate_performance_insights(aggregate_metrics)
            
            # Get content recommendations
            content_recommendations = await self._get_content_recommendations()
            
            return {
                "overview": {
                    "total_videos": len(recent_videos),
                    "total_views": aggregate_metrics.get("total_views", 0),
                    "avg_engagement_rate": aggregate_metrics.get("avg_engagement_rate", 0),
                    "avg_retention_rate": aggregate_metrics.get("avg_retention_rate", 0)
                },
                "recent_performance": recent_videos,
                "trending_topics": trending_topics,
                "insights": insights,
                "content_recommendations": content_recommendations,
                "performance_trends": await self._get_performance_trends()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise
    
    async def _get_video_metrics(self, video_id: str) -> PerformanceMetrics:
        """Get current video performance metrics"""
        try:
            if not self.youtube:
                # Return simulated metrics for demo
                return PerformanceMetrics(
                    view_count=15000,
                    like_count=450,
                    comment_count=89,
                    share_count=23,
                    watch_time_minutes=8500.0,
                    click_through_rate=0.045,
                    engagement_rate=0.032,
                    retention_rate=0.68
                )
            
            # Get video statistics from YouTube API
            video_response = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                raise ValueError(f"Video {video_id} not found")
            
            stats = video_response['items'][0]['statistics']
            
            # Calculate derived metrics
            view_count = int(stats.get('viewCount', 0))
            like_count = int(stats.get('likeCount', 0))
            comment_count = int(stats.get('commentCount', 0))
            
            # Estimate other metrics (would need YouTube Analytics API for actual data)
            engagement_rate = (like_count + comment_count) / max(view_count, 1)
            
            return PerformanceMetrics(
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                share_count=0,  # Not available in basic API
                watch_time_minutes=0.0,  # Requires Analytics API
                click_through_rate=0.0,  # Requires Analytics API
                engagement_rate=engagement_rate,
                retention_rate=0.0  # Requires Analytics API
            )
            
        except Exception as e:
            logger.error(f"Error getting video metrics: {str(e)}")
            # Return default metrics
            return PerformanceMetrics()
    
    async def _analyze_performance_gaps(
        self, 
        current_metrics: PerformanceMetrics, 
        target_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze gaps between current and target performance"""
        try:
            gaps = {}
            
            # Compare each metric
            for metric, target_value in target_metrics.items():
                current_value = getattr(current_metrics, metric, 0)
                gap = target_value - current_value
                gap_percentage = (gap / max(target_value, 1)) * 100
                
                gaps[metric] = {
                    "current": current_value,
                    "target": target_value,
                    "gap": gap,
                    "gap_percentage": gap_percentage,
                    "priority": "high" if gap_percentage > 50 else "medium" if gap_percentage > 20 else "low"
                }
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing performance gaps: {str(e)}")
            return {}
    
    async def _generate_optimization_recommendations(
        self, 
        video_id: str, 
        current_metrics: PerformanceMetrics,
        target_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze current performance
            if current_metrics.click_through_rate < 0.04:
                recommendations.append({
                    "type": "thumbnail_optimization",
                    "title": "Improve Thumbnail Design",
                    "description": "Current CTR is below 4%. Consider A/B testing new thumbnail designs.",
                    "priority": "high",
                    "estimated_impact": "15-25% CTR improvement"
                })
            
            if current_metrics.engagement_rate < 0.03:
                recommendations.append({
                    "type": "content_engagement",
                    "title": "Increase Engagement Elements",
                    "description": "Add more interactive elements, questions, and calls-to-action.",
                    "priority": "high",
                    "estimated_impact": "20-30% engagement improvement"
                })
            
            if current_metrics.retention_rate < 0.6:
                recommendations.append({
                    "type": "content_pacing",
                    "title": "Improve Content Pacing",
                    "description": "Optimize video pacing and add hooks to maintain viewer attention.",
                    "priority": "medium",
                    "estimated_impact": "10-20% retention improvement"
                })
            
            # Generate AI-powered recommendations
            ai_recommendations = await self._get_ai_recommendations(current_metrics, target_metrics)
            recommendations.extend(ai_recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {str(e)}")
            return []
    
    async def _get_ai_recommendations(
        self, 
        current_metrics: PerformanceMetrics,
        target_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get AI-powered optimization recommendations"""
        try:
            prompt = f"""
            Analyze these YouTube video performance metrics and provide optimization recommendations:
            
            Current Performance:
            - Views: {current_metrics.view_count}
            - Engagement Rate: {current_metrics.engagement_rate:.3f}
            - Retention Rate: {current_metrics.retention_rate:.3f}
            - Click-Through Rate: {current_metrics.click_through_rate:.3f}
            
            Target Metrics:
            {json.dumps(target_metrics, indent=2)}
            
            Provide 3-5 specific, actionable recommendations for improvement.
            Focus on the biggest gaps and highest-impact optimizations.
            
            Return as JSON array:
            [
                {{
                    "type": "recommendation_type",
                    "title": "Recommendation Title",
                    "description": "Detailed description",
                    "priority": "high/medium/low",
                    "estimated_impact": "Expected improvement"
                }}
            ]
            """
            
            response = await self._call_openai(prompt)
            recommendations = json.loads(response)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {str(e)}")
            return []
    
    async def _create_ab_test_variants(
        self, 
        video_id: str, 
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create A/B test variants for optimization"""
        try:
            ab_tests = []
            
            # Create thumbnail A/B tests
            thumbnail_recs = [r for r in recommendations if r["type"] == "thumbnail_optimization"]
            if thumbnail_recs:
                ab_tests.append({
                    "test_type": "thumbnail",
                    "variants": [
                        {"name": "Current", "description": "Current thumbnail"},
                        {"name": "Variant A", "description": "High-contrast design with bold text"},
                        {"name": "Variant B", "description": "Face-focused design with emotion"}
                    ],
                    "duration_days": 7,
                    "success_metric": "click_through_rate"
                })
            
            # Create title A/B tests
            title_recs = [r for r in recommendations if "title" in r["type"]]
            if title_recs:
                ab_tests.append({
                    "test_type": "title",
                    "variants": [
                        {"name": "Current", "description": "Current title"},
                        {"name": "Variant A", "description": "Question-based title"},
                        {"name": "Variant B", "description": "Benefit-focused title"}
                    ],
                    "duration_days": 5,
                    "success_metric": "click_through_rate"
                })
            
            return ab_tests
            
        except Exception as e:
            logger.error(f"Error creating A/B test variants: {str(e)}")
            return []
    
    async def _estimate_improvement(
        self, 
        current_metrics: PerformanceMetrics,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Estimate performance improvement from recommendations"""
        try:
            improvements = {}
            
            # Estimate CTR improvement
            ctr_improvements = [r for r in recommendations if "CTR" in r.get("estimated_impact", "")]
            if ctr_improvements:
                avg_improvement = 0.2  # 20% average improvement
                improvements["click_through_rate"] = current_metrics.click_through_rate * (1 + avg_improvement)
            
            # Estimate engagement improvement
            engagement_improvements = [r for r in recommendations if "engagement" in r.get("estimated_impact", "")]
            if engagement_improvements:
                avg_improvement = 0.25  # 25% average improvement
                improvements["engagement_rate"] = current_metrics.engagement_rate * (1 + avg_improvement)
            
            # Estimate retention improvement
            retention_improvements = [r for r in recommendations if "retention" in r.get("estimated_impact", "")]
            if retention_improvements:
                avg_improvement = 0.15  # 15% average improvement
                improvements["retention_rate"] = current_metrics.retention_rate * (1 + avg_improvement)
            
            return improvements
            
        except Exception as e:
            logger.error(f"Error estimating improvement: {str(e)}")
            return {}
    
    async def _get_recent_video_performance(self) -> List[Dict[str, Any]]:
        """Get recent video performance data"""
        try:
            # In a real implementation, this would query the database
            # For demo, return simulated data
            return [
                {
                    "video_id": "video_001",
                    "title": "Quadratic Equations Made Easy",
                    "views": 25000,
                    "engagement_rate": 0.045,
                    "retention_rate": 0.72,
                    "upload_date": "2024-01-15"
                },
                {
                    "video_id": "video_002",
                    "title": "Calculus Fundamentals",
                    "views": 18000,
                    "engagement_rate": 0.038,
                    "retention_rate": 0.68,
                    "upload_date": "2024-01-12"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent video performance: {str(e)}")
            return []
    
    async def _calculate_aggregate_metrics(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate performance metrics"""
        try:
            if not videos:
                return {}
            
            total_views = sum(v.get("views", 0) for v in videos)
            avg_engagement = sum(v.get("engagement_rate", 0) for v in videos) / len(videos)
            avg_retention = sum(v.get("retention_rate", 0) for v in videos) / len(videos)
            
            return {
                "total_views": total_views,
                "avg_engagement_rate": avg_engagement,
                "avg_retention_rate": avg_retention,
                "total_videos": len(videos)
            }
            
        except Exception as e:
            logger.error(f"Error calculating aggregate metrics: {str(e)}")
            return {}
    
    async def _get_trending_topics(self) -> List[str]:
        """Get trending topics in educational content"""
        try:
            # In a real implementation, this would analyze trending topics
            # For demo, return simulated trending topics
            return [
                "Quadratic Equations",
                "Organic Chemistry",
                "Trigonometry",
                "Physics Waves",
                "Calculus Integration"
            ]
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
            return []
    
    async def _generate_performance_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance insights"""
        try:
            insights = []
            
            if metrics.get("avg_engagement_rate", 0) > 0.04:
                insights.append("Engagement rates are above average - content is resonating well with audience")
            
            if metrics.get("avg_retention_rate", 0) > 0.7:
                insights.append("High retention rates indicate strong content quality and pacing")
            
            if metrics.get("total_views", 0) > 50000:
                insights.append("Strong viewership indicates effective content strategy")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating performance insights: {str(e)}")
            return []
    
    async def _get_content_recommendations(self) -> List[Dict[str, Any]]:
        """Get content creation recommendations"""
        try:
            return [
                {
                    "topic": "Advanced Calculus",
                    "priority": "high",
                    "estimated_views": 30000,
                    "reason": "High search volume, low competition"
                },
                {
                    "topic": "Chemistry Reactions",
                    "priority": "medium",
                    "estimated_views": 22000,
                    "reason": "Trending topic with good engagement potential"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting content recommendations: {str(e)}")
            return []
    
    async def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time"""
        try:
            # Simulate trend data
            return {
                "views_trend": [15000, 18000, 22000, 25000, 28000],
                "engagement_trend": [0.035, 0.038, 0.042, 0.045, 0.048],
                "retention_trend": [0.65, 0.68, 0.70, 0.72, 0.74],
                "period": "last_5_weeks"
            }
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {str(e)}")
            return {}
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with error handling"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a YouTube optimization expert specializing in educational content performance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise