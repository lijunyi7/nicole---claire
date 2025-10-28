#!/usr/bin/env python3
"""
Example script showing how to generate frames with a custom background image.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from core.video_frame_generator import VideoFrameGenerator

def main():
    """Demonstrate using a custom background image."""
    
    # Example 1: Use default gradient background
    print("1. Generating frame with default gradient background...")
    generator_default = VideoFrameGenerator()
    
    output_dir = Path(__file__).parent.parent / "outputs" / "frames"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    test_text = "Welcome to our AI Education Platform! This is a test frame with gradient background."
    output_file = output_dir / "example_gradient.png"
    generator_default.create_frame(test_text, str(output_file), font_size=48)
    print(f"✅ Generated: {output_file}")
    
    # Example 2: Use custom background (background_edu.jpg)
    print("\n2. Generating frame with custom background (background_edu.jpg)...")
    custom_bg_path = Path(__file__).parent.parent.parent / "background_edu.jpg"
    if custom_bg_path.exists():
        generator_custom = VideoFrameGenerator(background_path=str(custom_bg_path))
        
        test_text2 = "Hello! This frame uses the background_edu.jpg image with educational content."
        output_file2 = output_dir / "example_custom.png"
        generator_custom.create_frame(test_text2, str(output_file2), font_size=48)
        print(f"✅ Generated: {output_file2}")
    else:
        print(f"⚠️  Background image not found at: {custom_bg_path}")
    
    print("\n💡 The app.py is already configured to use background_edu.jpg!")
    print("   All generated frames will automatically use this background image.")

if __name__ == "__main__":
    main()

