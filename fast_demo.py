#!/usr/bin/env python3
"""
FAST YouTube Video Generation Demo
Creates real video content in seconds
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Create output directory
os.makedirs("output/fast", exist_ok=True)

print("🚀 FAST VIDEO GENERATION")
print("Creating Grade 10 Physics video...")

# Generate 3 slides instantly
slides = [
    ("Newton's Laws", "Physics Grade 10", "#1e40af"),
    ("F = ma", "Force = Mass × Acceleration", "#dc2626"), 
    ("Practice Problems", "Solve & Master Physics!", "#059669")
]

video_files = []
for i, (title, subtitle, color) in enumerate(slides, 1):
    # Create slide
    img = Image.new('RGB', (1280, 720), color=color)
    draw = ImageDraw.Draw(img)
    
    # Add text
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except:
        font_big = font_small = ImageFont.load_default()
    
    # Center title
    if font_big:
        bbox = draw.textbbox((0, 0), title, font=font_big)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((1280-w)//2, 250), title, fill='white', font=font_big)
        
        bbox2 = draw.textbbox((0, 0), subtitle, font=font_small)
        w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        draw.text(((1280-w2)//2, 400), subtitle, fill='white', font=font_small)
    
    filename = f"output/fast/slide_{i}.png"
    img.save(filename)
    video_files.append(filename)
    print(f"✅ Slide {i}: {title}")

# Create animated GIF
try:
    images = [Image.open(f) for f in video_files]
    gif_path = "output/fast/physics_video.gif"
    images[0].save(gif_path, save_all=True, append_images=images[1:], duration=1500, loop=0)
    
    size = os.path.getsize(gif_path)
    print(f"🎬 VIDEO CREATED: {gif_path}")
    print(f"📁 Size: {size//1024} KB")
    print(f"⏱️ Duration: 4.5 seconds")
    print(f"📐 Resolution: 1280×720 HD")
    print("🚀 READY TO VIEW!")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 FAST DEMO COMPLETE!")
print("📱 Open the GIF file to see your video!")