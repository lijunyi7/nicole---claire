"""
Video generation module using MoviePy plugin.
Combines audio files and image frames into video files.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Try new moviepy 2.x API first
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
    MOVIEPY_VERSION = 2
except ImportError:
    try:
        # Fallback to moviepy 1.x API
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
        MOVIEPY_AVAILABLE = True
        MOVIEPY_VERSION = 1
    except ImportError as e:
        MOVIEPY_AVAILABLE = False
        MOVIEPY_VERSION = 0
        print(f"Warning: MoviePy import failed: {e}")
        print("Install with: pip install moviepy")


class VideoGenerator:
    """Generates videos by combining audio files and image frames."""
    
    def __init__(self):
        """Initialize the video generator."""
        if not MOVIEPY_AVAILABLE:
            raise RuntimeError(
                "MoviePy is required for video generation. "
                "Please install it with: pip install moviepy"
            )
    
    def create_video_from_audio_and_frame(
        self,
        audio_path: str,
        frame_path: str,
        output_path: str,
        fps: int = 24
    ) -> str:
        """
        Create a video from a single audio file and frame.
        
        Args:
            audio_path: Path to audio file (MP3, WAV, etc.)
            frame_path: Path to frame image (PNG, JPG, etc.)
            output_path: Path to save the output video
            fps: Frames per second for the video (default: 24)
            
        Returns:
            Path to the generated video file
        """
        try:
            # Load the audio file first to get duration
            audio_clip = AudioFileClip(audio_path)
            
            # Load the frame image with duration
            if MOVIEPY_VERSION == 2:
                # MoviePy 2.x API - different approach
                from moviepy import VideoClip
                # Load image and set duration
                frame_clip = ImageClip(frame_path)
                frame_clip = frame_clip.with_duration(audio_clip.duration).with_fps(fps)
                # Set audio
                video_clip = frame_clip.with_audio(audio_clip)
            else:
                # MoviePy 1.x API
                frame_clip = ImageClip(frame_path).set_duration(audio_clip.duration)
                video_clip = frame_clip.set_audio(audio_clip).set_fps(fps)
            
            # Write the video file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if MOVIEPY_VERSION == 2:
                # MoviePy 2.x API
                video_clip.write_videofile(
                    str(output_file),
                    codec='libx264',
                    audio_codec='aac',
                    fps=fps
                )
            else:
                # MoviePy 1.x API
                video_clip.write_videofile(
                    str(output_file),
                    codec='libx264',
                    audio_codec='aac',
                    fps=fps,
                    verbose=False,
                    logger=None
                )
            
            # Clean up
            frame_clip.close()
            audio_clip.close()
            video_clip.close()
            
            print(f"Generated video: {output_file}")
            return str(output_file)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate video: {e}") from e
    
    def generate_script_videos(
        self,
        script_data: Dict[str, Any],
        audio_dir: str,
        frames_dir: str,
        output_dir: str,
        script_id: str = None
    ) -> List[str]:
        """
        Generate videos for all sections in a script.
        
        Args:
            script_data: The script data containing narrations
            audio_dir: Directory containing audio files
            frames_dir: Directory containing frame files
            output_dir: Directory to save video files
            script_id: Unique identifier for this script
            
        Returns:
            List of generated video file paths (basenames)
        """
        video_files = []
        audio_path = Path(audio_dir)
        frames_path = Path(frames_dir)
        output_path = Path(output_dir)
        
        # Create unique prefix based on script_id or use generic
        if script_id:
            prefix = f"{script_id}_"
        else:
            prefix = ""
        
        # Define sections to process
        sections_to_process = [
            ("intro", "narration", f"{prefix}intro_narration.mp3", f"{prefix}intro_narration.png"),
            ("explanation", "narration", f"{prefix}explanation_narration.mp3", f"{prefix}explanation_narration.png"),
            ("practice_mcq", "question", f"{prefix}practice_mcq_question.mp3", f"{prefix}practice_mcq_question.png"),
            ("practice_mcq", "explanation", f"{prefix}practice_mcq_explanation.mp3", f"{prefix}practice_mcq_explanation.png"),
            ("summary", "narration", f"{prefix}summary_narration.mp3", f"{prefix}summary_narration.png")
        ]
        
        for section, field, audio_filename, frame_filename in sections_to_process:
            # Check if this section exists in the script
            if section not in script_data:
                continue
                
            if field == "narration" and "narration" not in script_data[section]:
                continue
            if field == "question" and "question" not in script_data.get("practice_mcq", {}):
                continue
            if field == "explanation" and "explanation" not in script_data.get("practice_mcq", {}):
                continue
            
            # Check if audio and frame files exist
            audio_file = audio_path / audio_filename
            frame_file = frames_path / frame_filename
            
            if not audio_file.exists() or not frame_file.exists():
                print(f"Warning: Missing files for {section}.{field}")
                print(f"  Audio: {audio_file.exists()}")
                print(f"  Frame: {frame_file.exists()}")
                continue
            
            try:
                # Create video filename
                video_filename = audio_filename.replace(".mp3", ".mp4")
                video_path = output_path / video_filename
                
                # Generate video
                self.create_video_from_audio_and_frame(
                    str(audio_file),
                    str(frame_file),
                    str(video_path)
                )
                
                video_files.append(video_filename)  # Return basename
                
            except Exception as e:
                print(f"Warning: Failed to generate video for {section}.{field}: {e}")
        
        return video_files
    
    def concatenate_videos(
        self,
        video_paths: List[str],
        output_path: str,
        fps: int = 24
    ) -> str:
        """
        Concatenate multiple videos into a single video.
        
        Args:
            video_paths: List of paths to video files
            output_path: Path to save the concatenated video
            fps: Frames per second for the video
            
        Returns:
            Path to the concatenated video file
        """
        try:
            # Load all video clips
            clips = []
            for video_path in video_paths:
                if Path(video_path).exists():
                    clip = ImageClip(video_path).set_fps(fps)
                    audio = AudioFileClip(video_path)
                    clip = clip.set_audio(audio).set_duration(audio.duration)
                    clips.append(clip)
            
            if not clips:
                raise ValueError("No valid video clips to concatenate")
            
            # Concatenate clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Write the final video
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            final_video.write_videofile(
                str(output_file),
                codec='libx264',
                audio_codec='aac',
                fps=fps,
                verbose=False,
                logger=None
            )
            
            # Clean up
            for clip in clips:
                clip.close()
            final_video.close()
            
            return str(output_file)
            
        except Exception as e:
            raise RuntimeError(f"Failed to concatenate videos: {e}") from e
    
    def update_script_with_videos(
        self,
        script_data: Dict[str, Any],
        video_files: List[str]
    ) -> Dict[str, Any]:
        """
        Update script data with video file paths (basenames only).
        
        Args:
            script_data: Original script data
            video_files: List of video filenames
            
        Returns:
            Updated script data with video paths
        """
        updated_script = script_data.copy()
        
        # Build a mapping from filename -> logical key
        video_mapping = {}
        for video_file in video_files:
            if "intro_narration" in video_file:
                video_mapping["intro_video"] = video_file
            elif "explanation_narration" in video_file:
                video_mapping["explanation_video"] = video_file
            elif "practice_mcq_question" in video_file:
                video_mapping["practice_mcq_question_video"] = video_file
            elif "practice_mcq_explanation" in video_file:
                video_mapping["practice_mcq_explanation_video"] = video_file
            elif "summary_narration" in video_file:
                video_mapping["summary_video"] = video_file
        
        # Add video basenames to sections
        if "intro_video" in video_mapping and "intro" in updated_script:
            updated_script["intro"]["video"] = video_mapping["intro_video"]
        
        if "explanation_video" in video_mapping and "explanation" in updated_script:
            updated_script["explanation"]["video"] = video_mapping["explanation_video"]
        
        if "practice_mcq_question_video" in video_mapping and "practice_mcq" in updated_script:
            if "video" not in updated_script["practice_mcq"]:
                updated_script["practice_mcq"]["video"] = {}
            updated_script["practice_mcq"]["video"]["question"] = video_mapping["practice_mcq_question_video"]
        
        if "practice_mcq_explanation_video" in video_mapping and "practice_mcq" in updated_script:
            if "video" not in updated_script["practice_mcq"]:
                updated_script["practice_mcq"]["video"] = {}
            updated_script["practice_mcq"]["video"]["explanation"] = video_mapping["practice_mcq_explanation_video"]
        
        if "summary_video" in video_mapping and "summary" in updated_script:
            updated_script["summary"]["video"] = video_mapping["summary_video"]
        
        # Update metadata
        if "metadata" not in updated_script:
            updated_script["metadata"] = {}
        
        updated_script["metadata"]["videos_generated"] = True
        updated_script["metadata"]["video_files"] = list(video_mapping.values())
        
        return updated_script


def main():
    """Demo function to test video generation."""
    if not MOVIEPY_AVAILABLE:
        print("❌ MoviePy not available. Install with: pip install moviepy")
        return
    
    try:
        # Initialize video generator
        generator = VideoGenerator()
        
        print("🎬 Video Generator Demo")
        print("=" * 40)
        
        # This would require actual audio and frame files
        print("✅ Video generator initialized successfully")
        print("   Run the web app to generate videos from scripts")
        
    except RuntimeError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

