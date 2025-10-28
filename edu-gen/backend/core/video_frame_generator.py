"""
Video frame generation module using PIL.
Generates image frames for educational script narrations.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class VideoFrameGenerator:
    """Generates video frames with text overlays for educational scripts."""
    
    def __init__(self, background_path: str = None, width: int = 1920, height: int = 1080):
        """
        Initialize the video frame generator.
        
        Args:
            background_path: Path to background image (if None, creates gradient background)
            width: Frame width in pixels (default: 1920)
            height: Frame height in pixels (default: 1080)
        """
        self.width = width
        self.height = height
        
        if background_path and Path(background_path).exists():
            self.background_path = background_path
            self.use_custom_bg = True
        else:
            self.background_path = None
            self.use_custom_bg = False
    
    def _get_background_image(self) -> Image.Image:
        """
        Get background image (custom or generated gradient).
        
        Returns:
            PIL Image object
        """
        if self.use_custom_bg:
            bg = Image.open(self.background_path).convert("RGB")
            # Resize to match frame dimensions
            bg = bg.resize((self.width, self.height), Image.Resampling.LANCZOS)
        else:
            # Create a gradient background (blue to purple)
            bg = self._create_gradient_background()
        
        return bg
    
    def _create_gradient_background(self) -> Image.Image:
        """
        Create a gradient background image.
        
        Returns:
            PIL Image with gradient background
        """
        bg = Image.new("RGB", (self.width, self.height), (30, 60, 120))
        draw = ImageDraw.Draw(bg)
        
        # Create a simple gradient effect
        for y in range(self.height):
            # Blend from dark blue to purple
            r = int(30 + (y / self.height) * 40)
            g = int(60 + (y / self.height) * 30)
            b = int(120 + (y / self.height) * 60)
            color = (r, g, b)
            draw.line([(0, y), (self.width, y)], fill=color, width=1)
        
        return bg
    
    def _get_font(self, size: int = 48) -> ImageFont.FreeTypeFont:
        """
        Get font for text rendering.
        
        Args:
            size: Font size
            
        Returns:
            PIL Font object
        """
        try:
            # Try to use system fonts
            # macOS
            if os.path.exists("/System/Library/Fonts/Helvetica.ttc"):
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
            # Linux
            elif os.path.exists("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
            # Windows or fallback
            else:
                font = ImageFont.load_default()
        except Exception:
            # Fallback to default font
            font = ImageFont.load_default()
        
        return font
    
    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> List[str]:
        """
        Wrap text to fit within max_width.
        
        Args:
            text: Text to wrap
            font: Font object
            max_width: Maximum width in pixels
            
        Returns:
            List of wrapped text lines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Try adding the word
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (100, 100))).textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def create_frame(self, text: str, output_path: str, font_size: int = 48, 
                     max_width_ratio: float = 0.8) -> str:
        """
        Create a single frame with text overlay.
        
        Args:
            text: Text to display on the frame
            output_path: Path to save the frame
            font_size: Size of the font (default: 48)
            max_width_ratio: Ratio of frame width to use for text (default: 0.8)
            
        Returns:
            Path to the generated frame
        """
        # Load background
        bg = self._get_background_image()
        
        # Create drawing context
        draw = ImageDraw.Draw(bg)
        
        # Get font
        font = self._get_font(font_size)
        
        # Wrap text to fit within frame
        max_text_width = int(self.width * max_width_ratio)
        text_lines = self._wrap_text(text, font, max_text_width)
        
        # Calculate total text height
        total_text_height = 0
        line_heights = []
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            line_heights.append(line_height)
            total_text_height += line_height
        
        # Calculate starting y position (centered vertically)
        start_y = (self.height - total_text_height - len(text_lines) * 20) // 2
        
        # Draw each line
        current_y = start_y
        for i, line in enumerate(text_lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Center horizontally
            x = (self.width - text_width) // 2
            y = current_y
            
            # Draw white text with subtle outline for readability
            # Draw outline (black)
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x + adj, y + adj2), line, fill="black", font=font)
            
            # Draw main text (white)
            draw.text((x, y), line, fill="white", font=font)
            
            current_y += line_heights[i] + 20  # Add spacing between lines
        
        # Save frame
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        bg.save(output_file)
        
        return str(output_file)
    
    def generate_script_frames(self, script_data: Dict[str, Any], output_dir: str, 
                               script_id: str = None) -> List[str]:
        """
        Generate frames for all narrations in a script.
        
        Args:
            script_data: The script data containing narrations
            output_dir: Directory to save frame files
            script_id: Unique identifier for this script
            
        Returns:
            List of generated frame file paths
        """
        frame_files = []
        output_path = Path(output_dir)
        
        # Create unique prefix based on script_id or use generic
        if script_id:
            prefix = f"{script_id}_"
        else:
            prefix = ""
        
        # Generate frames for each section
        sections_to_process = [
            ("intro", "narration", f"{prefix}intro_narration.png"),
            ("explanation", "narration", f"{prefix}explanation_narration.png"),
            ("practice_mcq", "question", f"{prefix}practice_mcq_question.png"),
            ("practice_mcq", "explanation", f"{prefix}practice_mcq_explanation.png"),
            ("summary", "narration", f"{prefix}summary_narration.png")
        ]
        
        for section, field, filename in sections_to_process:
            if section in script_data and field in script_data[section]:
                text = script_data[section][field]
                if text and text.strip():  # Only process non-empty text
                    frame_path = output_path / filename
                    try:
                        generated_path = self.create_frame(text, str(frame_path))
                        frame_files.append(Path(generated_path).name)  # Return basename
                        print(f"Generated frame: {generated_path}")
                    except Exception as e:
                        print(f"Warning: Failed to generate frame for {section}.{field}: {e}")
        
        return frame_files
    
    def update_script_with_frames(self, script_data: Dict[str, Any], frame_files: List[str]) -> Dict[str, Any]:
        """
        Update script data with frame file paths (basenames only).
        
        Args:
            script_data: Original script data
            frame_files: List of frame filenames
            
        Returns:
            Updated script data with frame paths
        """
        updated_script = script_data.copy()
        
        # Build a mapping from filename -> logical key
        frame_mapping = {}
        for frame_file in frame_files:
            if "intro_narration" in frame_file:
                frame_mapping["intro_frame"] = frame_file
            elif "explanation_narration" in frame_file:
                frame_mapping["explanation_frame"] = frame_file
            elif "practice_mcq_question" in frame_file:
                frame_mapping["practice_mcq_question_frame"] = frame_file
            elif "practice_mcq_explanation" in frame_file:
                frame_mapping["practice_mcq_explanation_frame"] = frame_file
            elif "summary_narration" in frame_file:
                frame_mapping["summary_frame"] = frame_file
        
        # Add frame basenames to sections
        if "intro_frame" in frame_mapping and "intro" in updated_script:
            updated_script["intro"]["frame"] = frame_mapping["intro_frame"]
        
        if "explanation_frame" in frame_mapping and "explanation" in updated_script:
            updated_script["explanation"]["frame"] = frame_mapping["explanation_frame"]
        
        if "practice_mcq_question_frame" in frame_mapping and "practice_mcq" in updated_script:
            if "frame" not in updated_script["practice_mcq"]:
                updated_script["practice_mcq"]["frame"] = {}
            updated_script["practice_mcq"]["frame"]["question"] = frame_mapping["practice_mcq_question_frame"]
        
        if "practice_mcq_explanation_frame" in frame_mapping and "practice_mcq" in updated_script:
            if "frame" not in updated_script["practice_mcq"]:
                updated_script["practice_mcq"]["frame"] = {}
            updated_script["practice_mcq"]["frame"]["explanation"] = frame_mapping["practice_mcq_explanation_frame"]
        
        if "summary_frame" in frame_mapping and "summary" in updated_script:
            updated_script["summary"]["frame"] = frame_mapping["summary_frame"]
        
        # Update metadata
        if "metadata" not in updated_script:
            updated_script["metadata"] = {}
        
        updated_script["metadata"]["frames_generated"] = True
        updated_script["metadata"]["frame_files"] = list(frame_mapping.values())
        
        return updated_script


def main():
    """Demo function to test frame generation."""
    try:
        # Initialize frame generator
        generator = VideoFrameGenerator()
        
        print("🖼️  Video Frame Generator Demo")
        print("=" * 40)
        print(f"Frame dimensions: {generator.width}x{generator.height}")
        
        # Test text
        test_text = "Welcome to our AI Education Platform! This is a test frame generation."
        
        # Create output directory
        output_dir = Path(__file__).parent.parent / "outputs" / "frames"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate test frame
        output_file = output_dir / "test_frame.png"
        generated_path = generator.create_frame(test_text, str(output_file))
        
        print(f"✅ Test frame generated: {generated_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

