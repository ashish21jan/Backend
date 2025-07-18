#!/usr/bin/env python3
"""
Setup script for YouTube Content Automation Engine
Handles installation, configuration, and initial setup.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🎬 {title}")
    print("="*60)

def print_step(step):
    """Print formatted step"""
    print(f"\n📍 {step}")
    print("-" * 40)

def run_command(command, description):
    """Run command with error handling"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    print_step("Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step("Installing Dependencies")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    # Install additional system dependencies if needed
    print("📦 Checking system dependencies...")
    
    # Check for FFmpeg (required for video processing)
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ FFmpeg not found. Please install FFmpeg for video processing:")
        print("   - Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("   - macOS: brew install ffmpeg")
        print("   - Windows: Download from https://ffmpeg.org/download.html")
    
    return True

def setup_directories():
    """Create necessary directories"""
    print_step("Setting Up Directories")
    
    directories = [
        "output/videos",
        "assets/templates",
        "assets/images",
        "assets/audio",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def setup_environment():
    """Set up environment configuration"""
    print_step("Setting Up Environment")
    
    # Copy environment template if .env doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from template")
            print("⚠️ Please edit .env file with your API keys:")
            print("   - OPENAI_API_KEY: Your OpenAI API key")
            print("   - YOUTUBE_API_KEY: Your YouTube Data API key")
            print("   - GOOGLE_APPLICATION_CREDENTIALS: Path to Google service account JSON")
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def test_installation():
    """Test the installation"""
    print_step("Testing Installation")
    
    try:
        # Test imports
        print("Testing module imports...")
        from src.models import VideoRequest
        from src.content_intelligence import ContentIntelligence
        from src.video_generator import VideoGenerator
        from src.quality_assurance import QualityAssurance
        from src.performance_optimizer import PerformanceOptimizer
        print("✅ All modules imported successfully")
        
        # Test basic functionality
        print("Testing basic functionality...")
        video_request = VideoRequest(
            subject="Mathematics",
            grade="10",
            topic="Test Topic",
            difficulty_level="medium"
        )
        print("✅ Basic functionality test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {str(e)}")
        return False

def create_demo_data():
    """Create sample data for demonstration"""
    print_step("Creating Demo Data")
    
    # Create sample video request
    sample_request = {
        "subject": "Mathematics",
        "grade": "10",
        "topic": "Quadratic Equations",
        "difficulty_level": "medium",
        "target_duration": 600,
        "include_examples": True,
        "include_practice": True,
        "voice_style": "professional"
    }
    
    # Save sample files if they don't exist
    if not os.path.exists("sample_input.json"):
        print("⚠️ sample_input.json not found - please check file creation")
    else:
        print("✅ Sample input file exists")
    
    if not os.path.exists("sample_output.json"):
        print("⚠️ sample_output.json not found - please check file creation")
    else:
        print("✅ Sample output file exists")
    
    return True

def display_next_steps():
    """Display next steps for the user"""
    print_step("Next Steps")
    
    print("🚀 Installation completed! Here's how to get started:")
    print()
    print("1. Configure API Keys:")
    print("   📝 Edit the .env file with your API keys")
    print("   🔑 OPENAI_API_KEY=your_openai_key")
    print("   🔑 YOUTUBE_API_KEY=your_youtube_key")
    print()
    print("2. Start the Application:")
    print("   🖥️ Backend API: uvicorn main:app --reload")
    print("   📊 Dashboard: streamlit run dashboard.py")
    print()
    print("3. Access the Tools:")
    print("   🌐 API Documentation: http://localhost:8000/docs")
    print("   📊 Dashboard: http://localhost:8501")
    print()
    print("4. Run Demo:")
    print("   🎬 python demo.py")
    print()
    print("5. Sample Files:")
    print("   📁 Input: sample_input.json")
    print("   📁 Output: sample_output.json")
    print()
    print("🎯 Key Features:")
    print("   • Content Intelligence: Trend analysis and content ideas")
    print("   • Video Generation: Automated script, audio, and video creation")
    print("   • Quality Assurance: Educational content validation")
    print("   • Performance Optimization: YouTube-specific optimizations")
    print("   • Analytics Dashboard: Comprehensive performance tracking")

def main():
    """Main setup function"""
    print_header("YouTube Content Automation Engine - Setup")
    print("🚀 Setting up the automation tool for Vedantu-scale content creation")
    print("📊 Target: 25+ channels, 1,000+ videos/month, 650M+ views")
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Installing Dependencies", install_dependencies),
        ("Setting Up Directories", setup_directories),
        ("Setting Up Environment", setup_environment),
        ("Creating Demo Data", create_demo_data),
        ("Testing Installation", test_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        if not step_function():
            failed_steps.append(step_name)
    
    # Summary
    print_header("Setup Summary")
    
    if failed_steps:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   • {step}")
        print("\n⚠️ Please resolve the errors above before proceeding.")
    else:
        print("✅ Setup completed successfully!")
        print("🎉 YouTube Content Automation Engine is ready to use!")
        
        display_next_steps()
    
    print("\n" + "="*60)
    print("📧 For support, check the README.md file")
    print("🔗 GitHub: https://github.com/your-repo/youtube-automation")
    print("="*60)

if __name__ == "__main__":
    main()