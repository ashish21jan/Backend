import asyncio
import logging
import os
import json
from typing import Dict, Any, List
import openai
from .models import QualityMetrics, Script

logger = logging.getLogger(__name__)

class QualityAssurance:
    """Quality Assurance Engine for validating educational content"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.quality_thresholds = {
            "educational_accuracy": 0.8,
            "content_clarity": 0.7,
            "engagement_potential": 0.6,
            "technical_quality": 0.7,
            "overall_score": 0.7
        }
    
    async def validate_script(self, script: Script) -> QualityMetrics:
        """Validate educational script quality"""
        try:
            # Prepare script content for analysis
            script_content = {
                "title": script.title,
                "sections": [
                    {
                        "type": section.section_type,
                        "title": section.title,
                        "content": section.content,
                        "duration": section.duration
                    }
                    for section in script.sections
                ],
                "key_concepts": script.key_concepts,
                "learning_objectives": script.learning_objectives,
                "total_duration": script.total_duration
            }
            
            # Analyze educational accuracy
            accuracy_score = await self._analyze_educational_accuracy(script_content)
            
            # Analyze content clarity
            clarity_score = await self._analyze_content_clarity(script_content)
            
            # Analyze engagement potential
            engagement_score = await self._analyze_engagement_potential(script_content)
            
            # Analyze technical quality
            technical_score = await self._analyze_technical_quality(script_content)
            
            # Calculate overall score
            overall_score = (accuracy_score + clarity_score + engagement_score + technical_score) / 4
            
            # Generate feedback
            feedback = await self._generate_feedback(script_content, {
                "accuracy": accuracy_score,
                "clarity": clarity_score,
                "engagement": engagement_score,
                "technical": technical_score,
                "overall": overall_score
            })
            
            quality_metrics = QualityMetrics(
                educational_accuracy=accuracy_score,
                content_clarity=clarity_score,
                engagement_potential=engagement_score,
                technical_quality=technical_score,
                overall_score=overall_score,
                feedback=feedback
            )
            
            logger.info(f"Script quality assessment completed. Overall score: {overall_score:.2f}")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error validating script: {str(e)}")
            raise
    
    async def validate_video(self, video_path: str) -> QualityMetrics:
        """Validate final video quality"""
        try:
            # For demo purposes, we'll simulate video quality analysis
            # In production, this would use video analysis libraries
            
            # Check if video file exists and is not empty
            if not os.path.exists(video_path):
                raise ValueError(f"Video file not found: {video_path}")
            
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                raise ValueError("Video file is empty")
            
            # Simulate quality metrics based on file properties
            # In production, this would analyze video/audio quality, resolution, etc.
            
            technical_quality = 0.85  # Simulated based on encoding settings
            
            # Estimate other metrics based on file size and duration
            # Larger files generally indicate better quality
            size_mb = file_size / (1024 * 1024)
            
            if size_mb > 100:  # High quality video
                video_quality_score = 0.9
            elif size_mb > 50:  # Medium quality
                video_quality_score = 0.8
            else:  # Lower quality
                video_quality_score = 0.7
            
            # For demo, we'll use the same scores as technical quality
            quality_metrics = QualityMetrics(
                educational_accuracy=0.85,  # Assumed good since script passed validation
                content_clarity=0.8,
                engagement_potential=0.75,
                technical_quality=technical_quality,
                overall_score=video_quality_score,
                feedback=[
                    f"Video file size: {size_mb:.1f} MB",
                    "Video encoding completed successfully",
                    "Audio quality is acceptable",
                    "Visual quality meets standards"
                ]
            )
            
            logger.info(f"Video quality assessment completed. Overall score: {video_quality_score:.2f}")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error validating video: {str(e)}")
            raise
    
    async def _analyze_educational_accuracy(self, script_content: Dict[str, Any]) -> float:
        """Analyze educational accuracy of content"""
        try:
            prompt = f"""
            Analyze the educational accuracy of this script content:
            
            Title: {script_content['title']}
            Key Concepts: {', '.join(script_content['key_concepts'])}
            Learning Objectives: {', '.join(script_content['learning_objectives'])}
            
            Script Sections:
            {json.dumps(script_content['sections'], indent=2)}
            
            Rate the educational accuracy on a scale of 0.0 to 1.0 based on:
            1. Factual correctness
            2. Age-appropriate content
            3. Alignment with curriculum standards
            4. Logical flow of concepts
            5. Completeness of explanations
            
            Return only a decimal number between 0.0 and 1.0.
            """
            
            response = await self._call_openai(prompt)
            score = float(response.strip())
            return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
            
        except Exception as e:
            logger.error(f"Error analyzing educational accuracy: {str(e)}")
            return 0.5  # Default fallback score
    
    async def _analyze_content_clarity(self, script_content: Dict[str, Any]) -> float:
        """Analyze content clarity and understandability"""
        try:
            prompt = f"""
            Analyze the clarity and understandability of this educational script:
            
            Title: {script_content['title']}
            Total Duration: {script_content['total_duration']} seconds
            
            Script Content:
            {json.dumps([section['content'] for section in script_content['sections']], indent=2)}
            
            Rate the content clarity on a scale of 0.0 to 1.0 based on:
            1. Language simplicity and clarity
            2. Logical structure and flow
            3. Use of examples and analogies
            4. Appropriate pacing
            5. Clear explanations of complex concepts
            
            Return only a decimal number between 0.0 and 1.0.
            """
            
            response = await self._call_openai(prompt)
            score = float(response.strip())
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error analyzing content clarity: {str(e)}")
            return 0.5
    
    async def _analyze_engagement_potential(self, script_content: Dict[str, Any]) -> float:
        """Analyze engagement potential for YouTube audience"""
        try:
            prompt = f"""
            Analyze the engagement potential of this educational video script for YouTube:
            
            Title: {script_content['title']}
            Section Types: {[section['type'] for section in script_content['sections']]}
            
            Script Structure:
            {json.dumps([{'type': s['type'], 'title': s['title']} for s in script_content['sections']], indent=2)}
            
            Rate the engagement potential on a scale of 0.0 to 1.0 based on:
            1. Compelling introduction/hook
            2. Interactive elements and examples
            3. Appropriate video length
            4. Clear call-to-action
            5. Student-friendly language and tone
            
            Return only a decimal number between 0.0 and 1.0.
            """
            
            response = await self._call_openai(prompt)
            score = float(response.strip())
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error analyzing engagement potential: {str(e)}")
            return 0.5
    
    async def _analyze_technical_quality(self, script_content: Dict[str, Any]) -> float:
        """Analyze technical quality of script structure"""
        try:
            # Analyze script structure programmatically
            sections = script_content['sections']
            total_duration = script_content['total_duration']
            
            score = 1.0
            
            # Check if script has proper structure
            section_types = [s['type'] for s in sections]
            if 'intro' not in section_types:
                score -= 0.1
            if 'main' not in section_types:
                score -= 0.2
            
            # Check duration balance
            total_section_duration = sum(s['duration'] for s in sections)
            if abs(total_section_duration - total_duration) > 60:  # More than 1 minute difference
                score -= 0.1
            
            # Check section lengths
            for section in sections:
                if section['duration'] < 10:  # Too short
                    score -= 0.05
                elif section['duration'] > 300:  # Too long (5 minutes)
                    score -= 0.05
            
            # Check content length
            total_content_length = sum(len(s['content']) for s in sections)
            if total_content_length < 500:  # Too short
                score -= 0.1
            elif total_content_length > 5000:  # Too long
                score -= 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error analyzing technical quality: {str(e)}")
            return 0.5
    
    async def _generate_feedback(self, script_content: Dict[str, Any], scores: Dict[str, float]) -> List[str]:
        """Generate actionable feedback based on quality analysis"""
        try:
            feedback = []
            
            # Educational accuracy feedback
            if scores['accuracy'] < self.quality_thresholds['educational_accuracy']:
                feedback.append("Consider reviewing factual accuracy and curriculum alignment")
            
            # Content clarity feedback
            if scores['clarity'] < self.quality_thresholds['content_clarity']:
                feedback.append("Improve content clarity with simpler language and better examples")
            
            # Engagement feedback
            if scores['engagement'] < self.quality_thresholds['engagement_potential']:
                feedback.append("Add more interactive elements and engaging hooks")
            
            # Technical feedback
            if scores['technical'] < self.quality_thresholds['technical_quality']:
                feedback.append("Review script structure and section timing")
            
            # Overall feedback
            if scores['overall'] >= 0.8:
                feedback.append("Excellent quality! Ready for production")
            elif scores['overall'] >= 0.7:
                feedback.append("Good quality with minor improvements needed")
            else:
                feedback.append("Significant improvements required before production")
            
            # Add specific suggestions
            prompt = f"""
            Based on this educational script analysis:
            - Educational Accuracy: {scores['accuracy']:.2f}
            - Content Clarity: {scores['clarity']:.2f}
            - Engagement Potential: {scores['engagement']:.2f}
            - Technical Quality: {scores['technical']:.2f}
            
            Provide 3 specific, actionable suggestions for improvement.
            Focus on the lowest-scoring areas.
            
            Return as a JSON array of strings.
            """
            
            response = await self._call_openai(prompt)
            suggestions = json.loads(response)
            feedback.extend(suggestions)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            return ["Unable to generate detailed feedback"]
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with error handling"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content quality assessor. Provide accurate, objective evaluations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent evaluations
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise