import asyncio
import json
import logging
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from .models import VideoRequest, Script, ScriptSection, VideoMetadata
from .database import Database

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Video Generation Engine for creating educational videos"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.output_dir = os.getenv("VIDEO_OUTPUT_DIR", "./output/videos")
        self.assets_dir = os.getenv("ASSETS_DIR", "./assets")
        self.db = Database()
        self.jobs = {}  # In-memory job tracking (use Redis in production)
        
        # Ensure output directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.assets_dir}/audio", exist_ok=True)
        os.makedirs(f"{self.assets_dir}/images", exist_ok=True)
        
    async def start_video_generation(self, video_request: VideoRequest) -> str:
        """Start a new video generation job"""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Job created",
            "created_at": datetime.now(),
            "video_request": video_request
        }
        
        logger.info(f"Started video generation job {job_id}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a video generation job"""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        return self.jobs[job_id]
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        progress: int, 
        message: str = "",
        video_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update job status"""
        if job_id in self.jobs:
            self.jobs[job_id].update({
                "status": status,
                "progress": progress,
                "message": message,
                "updated_at": datetime.now()
            })
            
            if video_url:
                self.jobs[job_id]["video_url"] = video_url
            if metadata:
                self.jobs[job_id]["metadata"] = metadata
    
    async def generate_script(self, video_request: VideoRequest) -> Script:
        """Generate educational script based on video request"""
        try:
            prompt = f"""
            Create a comprehensive educational script for a {video_request.target_duration}-second video on:
            
            Subject: {video_request.subject}
            Grade: {video_request.grade}
            Topic: {video_request.topic}
            Difficulty: {video_request.difficulty_level}
            Include Examples: {video_request.include_examples}
            Include Practice: {video_request.include_practice}
            
            Structure the script with these sections:
            1. Introduction (30-60 seconds) - Hook and overview
            2. Main Content (60-70% of video) - Core concepts
            3. Examples (if requested) - Worked examples
            4. Practice Problems (if requested) - Student exercises
            5. Conclusion (30-60 seconds) - Summary and next steps
            
            For each section, provide:
            - Clear, engaging narration text
            - Visual cues for what should be shown
            - Timing estimates
            - Key concepts covered
            
            Make it engaging, clear, and appropriate for Grade {video_request.grade} students.
            
            Return as JSON with this structure:
            {{
                "title": "Engaging video title",
                "total_duration": {video_request.target_duration},
                "sections": [
                    {{
                        "section_type": "intro",
                        "title": "Introduction",
                        "content": "Narration text...",
                        "duration": 60,
                        "visual_cues": ["Show title slide", "Display key formula"]
                    }}
                ],
                "key_concepts": ["concept1", "concept2"],
                "learning_objectives": ["Students will be able to..."]
            }}
            """
            
            response = await self._call_openai(prompt)
            script_data = json.loads(response)
            
            # Convert to Script model
            sections = []
            for section_data in script_data["sections"]:
                sections.append(ScriptSection(
                    section_type=section_data["section_type"],
                    title=section_data["title"],
                    content=section_data["content"],
                    duration=section_data["duration"],
                    visual_cues=section_data.get("visual_cues", [])
                ))
            
            script = Script(
                title=script_data["title"],
                total_duration=script_data["total_duration"],
                sections=sections,
                key_concepts=script_data["key_concepts"],
                learning_objectives=script_data["learning_objectives"]
            )
            
            logger.info(f"Generated script: {script.title}")
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise
    
    async def generate_voiceover(self, script: Script) -> str:
        """Generate voiceover audio from script"""
        try:
            # Combine all script content
            full_text = ""
            for section in script.sections:
                full_text += section.content + " "
            
            # Generate audio using gTTS
            tts = gTTS(text=full_text, lang='en', slow=False)
            audio_filename = f"voiceover_{uuid.uuid4().hex}.mp3"
            audio_path = os.path.join(self.assets_dir, "audio", audio_filename)
            
            tts.save(audio_path)
            logger.info(f"Generated voiceover: {audio_path}")
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Error generating voiceover: {str(e)}")
            raise
    
    async def generate_visuals(self, video_request: VideoRequest, script: Script) -> List[str]:
        """Generate visual assets for the video"""
        try:
            visual_assets = []
            
            # Generate title slide
            title_slide = await self._create_title_slide(script.title, video_request.subject)
            visual_assets.append(title_slide)
            
            # Generate content slides for each section
            for i, section in enumerate(script.sections):
                if section.section_type == "intro":
                    slide = await self._create_intro_slide(section.title, section.visual_cues)
                elif section.section_type == "main":
                    slide = await self._create_content_slide(section.title, section.visual_cues, i)
                elif section.section_type == "example":
                    slide = await self._create_example_slide(section.title, section.visual_cues, i)
                else:
                    slide = await self._create_generic_slide(section.title, section.visual_cues, i)
                
                visual_assets.append(slide)
            
            # Generate conclusion slide
            conclusion_slide = await self._create_conclusion_slide(script.key_concepts)
            visual_assets.append(conclusion_slide)
            
            logger.info(f"Generated {len(visual_assets)} visual assets")
            return visual_assets
            
        except Exception as e:
            logger.error(f"Error generating visuals: {str(e)}")
            raise
    
    async def assemble_video(self, script: Script, audio_path: str, visual_assets: List[str]) -> str:
        """Assemble final video from components"""
        try:
            # Load audio
            audio = AudioFileClip(audio_path)
            
            # Create video clips from images
            clips = []
            section_durations = [section.duration for section in script.sections]
            
            # Distribute visual assets across sections
            for i, (asset_path, duration) in enumerate(zip(visual_assets, section_durations)):
                if os.path.exists(asset_path):
                    # Create image clip
                    img_clip = ImageClip(asset_path, duration=duration)
                    img_clip = img_clip.resize((1280, 720))  # HD resolution
                    clips.append(img_clip)
            
            # Concatenate all clips
            if clips:
                video = concatenate_videoclips(clips)
                
                # Set audio
                if audio.duration > video.duration:
                    audio = audio.subclip(0, video.duration)
                elif video.duration > audio.duration:
                    video = video.subclip(0, audio.duration)
                
                final_video = video.set_audio(audio)
                
                # Export video
                video_filename = f"video_{uuid.uuid4().hex}.mp4"
                video_path = os.path.join(self.output_dir, video_filename)
                
                final_video.write_videofile(
                    video_path,
                    fps=24,
                    codec='libx264',
                    audio_codec='aac'
                )
                
                # Clean up
                audio.close()
                video.close()
                final_video.close()
                
                logger.info(f"Assembled video: {video_path}")
                return video_path
            else:
                raise ValueError("No visual assets available for video assembly")
                
        except Exception as e:
            logger.error(f"Error assembling video: {str(e)}")
            raise
    
    async def generate_metadata(self, video_request: VideoRequest, script: Script) -> VideoMetadata:
        """Generate YouTube metadata for the video"""
        try:
            prompt = f"""
            Generate YouTube metadata for an educational video:
            
            Title: {script.title}
            Subject: {video_request.subject}
            Grade: {video_request.grade}
            Topic: {video_request.topic}
            Key Concepts: {', '.join(script.key_concepts)}
            Learning Objectives: {', '.join(script.learning_objectives)}
            
            Create:
            1. SEO-optimized title (under 60 characters)
            2. Detailed description (include timestamps, key concepts, target audience)
            3. Relevant tags (15-20 tags)
            
            Focus on YouTube education best practices and SEO optimization.
            
            Return as JSON:
            {{
                "title": "...",
                "description": "...",
                "tags": ["tag1", "tag2", ...]
            }}
            """
            
            response = await self._call_openai(prompt)
            metadata_data = json.loads(response)
            
            metadata = VideoMetadata(
                title=metadata_data["title"],
                description=metadata_data["description"],
                tags=metadata_data["tags"],
                category_id=27,  # Education category
                language="en"
            )
            
            logger.info(f"Generated metadata for: {metadata.title}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating metadata: {str(e)}")
            raise
    
    async def _create_title_slide(self, title: str, subject: str) -> str:
        """Create title slide image"""
        try:
            # Create image
            img = Image.new('RGB', (1280, 720), color='#1e3a8a')  # Blue background
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fall back to default if not available
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                subject_font = ImageFont.truetype("arial.ttf", 32)
            except:
                title_font = ImageFont.load_default()
                subject_font = ImageFont.load_default()
            
            # Draw title
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1280 - title_width) // 2
            draw.text((title_x, 250), title, fill='white', font=title_font)
            
            # Draw subject
            subject_bbox = draw.textbbox((0, 0), subject, font=subject_font)
            subject_width = subject_bbox[2] - subject_bbox[0]
            subject_x = (1280 - subject_width) // 2
            draw.text((subject_x, 350), subject, fill='#fbbf24', font=subject_font)
            
            # Save image
            filename = f"title_slide_{uuid.uuid4().hex}.png"
            filepath = os.path.join(self.assets_dir, "images", filename)
            img.save(filepath)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating title slide: {str(e)}")
            raise
    
    async def _create_intro_slide(self, title: str, visual_cues: List[str]) -> str:
        """Create introduction slide"""
        return await self._create_generic_slide(title, visual_cues, 0, color='#059669')
    
    async def _create_content_slide(self, title: str, visual_cues: List[str], index: int) -> str:
        """Create content slide"""
        return await self._create_generic_slide(title, visual_cues, index, color='#7c3aed')
    
    async def _create_example_slide(self, title: str, visual_cues: List[str], index: int) -> str:
        """Create example slide"""
        return await self._create_generic_slide(title, visual_cues, index, color='#dc2626')
    
    async def _create_generic_slide(self, title: str, visual_cues: List[str], index: int, color: str = '#1e3a8a') -> str:
        """Create generic slide with title and visual cues"""
        try:
            # Create image
            img = Image.new('RGB', (1280, 720), color=color)
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                cue_font = ImageFont.truetype("arial.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                cue_font = ImageFont.load_default()
            
            # Draw title
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1280 - title_width) // 2
            draw.text((title_x, 100), title, fill='white', font=title_font)
            
            # Draw visual cues
            y_offset = 200
            for cue in visual_cues[:5]:  # Limit to 5 cues
                cue_bbox = draw.textbbox((0, 0), f"• {cue}", font=cue_font)
                cue_width = cue_bbox[2] - cue_bbox[0]
                cue_x = (1280 - cue_width) // 2
                draw.text((cue_x, y_offset), f"• {cue}", fill='#fbbf24', font=cue_font)
                y_offset += 60
            
            # Save image
            filename = f"slide_{index}_{uuid.uuid4().hex}.png"
            filepath = os.path.join(self.assets_dir, "images", filename)
            img.save(filepath)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating slide: {str(e)}")
            raise
    
    async def _create_conclusion_slide(self, key_concepts: List[str]) -> str:
        """Create conclusion slide with key concepts"""
        try:
            # Create image
            img = Image.new('RGB', (1280, 720), color='#065f46')
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                concept_font = ImageFont.truetype("arial.ttf", 28)
            except:
                title_font = ImageFont.load_default()
                concept_font = ImageFont.load_default()
            
            # Draw title
            title = "Key Takeaways"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1280 - title_width) // 2
            draw.text((title_x, 100), title, fill='white', font=title_font)
            
            # Draw key concepts
            y_offset = 200
            for concept in key_concepts[:6]:  # Limit to 6 concepts
                concept_bbox = draw.textbbox((0, 0), f"✓ {concept}", font=concept_font)
                concept_width = concept_bbox[2] - concept_bbox[0]
                concept_x = (1280 - concept_width) // 2
                draw.text((concept_x, y_offset), f"✓ {concept}", fill='#10b981', font=concept_font)
                y_offset += 50
            
            # Save image
            filename = f"conclusion_slide_{uuid.uuid4().hex}.png"
            filepath = os.path.join(self.assets_dir, "images", filename)
            img.save(filepath)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating conclusion slide: {str(e)}")
            raise
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with error handling"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator specializing in creating engaging video scripts for students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise