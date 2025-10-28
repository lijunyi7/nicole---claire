"""
Demo runner tool for the educational script generator.
Provides a complete workflow from topic to audio.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.generate_script import ScriptGenerator
from core.text_to_speech import TextToSpeechGenerator
from core.video_frame_generator import VideoFrameGenerator
from core.video_generator import VideoGenerator
from validation.validate_schema import SchemaValidator
from config.env_config import check_environment_setup


class DemoRunner:
    """Complete demo runner for educational script generation."""
    
    def __init__(self):
        """Initialize the demo runner with all required components."""
        self.script_generator = ScriptGenerator()
        self.validator = SchemaValidator()
        self.tts_generator = TextToSpeechGenerator(voice="nova")
        
        # Initialize frame generator with custom background
        backend_dir = Path(__file__).parent.parent
        background_path = backend_dir.parent / "background_edu.jpg"
        self.frame_generator = VideoFrameGenerator(background_path=str(background_path) if background_path.exists() else None)
        
        try:
            self.video_generator = VideoGenerator()
            self.video_enabled = True
        except RuntimeError:
            self.video_generator = None
            self.video_enabled = False
            print("⚠️  Video generation disabled (MoviePy not available)")
    
    def run_complete_workflow(self, topic: str, output_dir: str = None) -> Dict[str, str]:
        """
        Run the complete workflow from topic to script.
        
        Args:
            topic: The educational topic
            output_dir: Output directory (defaults to outputs/)
            
        Returns:
            Dictionary with paths to generated files
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "outputs"
        else:
            output_dir = Path(output_dir)
        
        results = {}
        
        try:
            print("Starting Educational Script Generation")
            print("=" * 50)
            print(f"Topic: {topic}")
            print()
            
            # Check environment setup
            if not check_environment_setup():
                raise Exception("Environment not properly configured. Please check your .env file.")
            
            # Step 1: Load prompt template
            print("📝 Step 1: Loading prompt template...")
            template_path = Path(__file__).parent.parent / "prompts" / "prompt_template_math.txt"
            with open(template_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            print("✅ Prompt template loaded")
            print()
            
            # Step 2: Generate script
            print("🤖 Step 2: Generating script with OpenAI...")
            script_data = self.script_generator.generate_script(topic, prompt_template)
            print("✅ Script generated")
            print()
            
            # Step 3: Validate script
            print("🔍 Step 3: Validating script against schema...")
            is_valid, errors = self.validator.validate_script(script_data)
            
            if not is_valid:
                print("❌ Script validation failed!")
                for error in errors:
                    print(f"  - {error}")
                raise Exception("Script validation failed")
            
            print("✅ Script validation passed")
            print()
            
            # Step 4: Generate audio files
            print("🎤 Step 4: Generating audio files...")
            safe_topic = topic.replace('：', '_').replace(' ', '_')[:50]
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_id = f"{safe_topic}_{timestamp}"
            
            audio_dir = output_dir / "audio"
            audio_files = self.tts_generator.generate_script_audio(script_data, str(audio_dir), script_id=script_id)
            updated_script = self.tts_generator.update_script_with_audio(script_data, audio_files)
            print(f"✅ Generated {len(audio_files)} audio files")
            print()
            
            # Step 5: Generate video frames
            print("🖼️  Step 5: Generating video frames...")
            frames_dir = output_dir / "frames"
            frame_files = self.frame_generator.generate_script_frames(script_data, str(frames_dir), script_id=script_id)
            updated_script = self.frame_generator.update_script_with_frames(updated_script, frame_files)
            print(f"✅ Generated {len(frame_files)} frames")
            print()
            
            # Step 6: Generate videos
            if self.video_enabled:
                print("🎬 Step 6: Generating videos...")
                videos_dir = output_dir / "videos"
                video_files = self.video_generator.generate_script_videos(
                    script_data,
                    str(audio_dir),
                    str(frames_dir),
                    str(videos_dir),
                    script_id=script_id
                )
                updated_script = self.video_generator.update_script_with_videos(updated_script, video_files)
                print(f"✅ Generated {len(video_files)} videos")
                results["videos"] = [str(videos_dir / vf) for vf in video_files]
            else:
                print("⚠️  Step 6: Skipping video generation (MoviePy not available)")
                video_files = []
            print()
            
            # Step 7: Save updated script
            print("💾 Step 7: Saving script with media references...")
            script_filename = f"{safe_topic}_{timestamp}.json"
            scripts_dir = output_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            script_path = scripts_dir / script_filename
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(updated_script, f, ensure_ascii=False, indent=2)
            results["script"] = str(script_path)
            results["audio_files"] = [str(audio_dir / af) for af in audio_files]
            results["frame_files"] = [str(frames_dir / ff) for ff in frame_files]
            print(f"✅ Script saved to: {script_path}")
            print()
            
            # Step 8: Show results
            print("📊 Step 5: Final Results")
            print("-" * 30)
            
            # Show script summary
            print("Script Summary:")
            print(f"  Topic: {script_data['metadata']['topic']}")
            print(f"  Language: {script_data['metadata']['language']}")
            print(f"  Estimated Duration: {script_data['metadata']['duration_estimate']}s")
            print()
            
            print("🎉 Complete workflow finished successfully!")
            return results
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            raise
    
    def show_script_preview(self, script_path: str) -> None:
        """
        Show a preview of the generated script.
        
        Args:
            script_path: Path to the script file
        """
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
            
            print("📖 Script Preview")
            print("=" * 50)
            
            # Show metadata
            metadata = script_data.get("metadata", {})
            print(f"Topic: {metadata.get('topic', 'Unknown')}")
            print(f"Language: {metadata.get('language', 'Unknown')}")
            print(f"Duration: {metadata.get('duration_estimate', 'Unknown')}s")
            print()
            
            # Show each section
            sections = ["intro", "explanation", "practice_mcq", "summary"]
            section_names = {
                "intro": "Introduction",
                "explanation": "Explanation", 
                "practice_mcq": "Practice Question",
                "summary": "Summary"
            }
            
            for section in sections:
                if section in script_data:
                    print(f"📝 {section_names[section]}:")
                    section_data = script_data[section]
                    
                    if "title" in section_data:
                        print(f"  Title: {section_data['title']}")
                    
                    if "narration" in section_data:
                        narration = section_data["narration"]
                        preview = narration[:100] + "..." if len(narration) > 100 else narration
                        print(f"  Narration: {preview}")
                    
                    if section == "practice_mcq":
                        if "question" in section_data:
                            print(f"  Question: {section_data['question']}")
                        if "options" in section_data:
                            print(f"  Options: {len(section_data['options'])} choices")
                        if "correct_answer" in section_data:
                            print(f"  Correct Answer: Option {section_data['correct_answer'] + 1}")
                    
                    print()
            
        except Exception as e:
            print(f"Error showing script preview: {e}")


def main():
    """Main demo function."""
    if len(sys.argv) < 2:
        print("Usage: python demo_runner.py <topic> [output_dir]")
        print("Example: python demo_runner.py '十以内减法：9 - 4'")
        print("Example: python demo_runner.py '十以内减法：9 - 4' /path/to/output")
        sys.exit(1)
    
    topic = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        runner = DemoRunner()
        results = runner.run_complete_workflow(topic, output_dir)
        
        print("\n" + "=" * 50)
        print("FINAL OUTPUTS")
        print("=" * 50)
        print(f"✅ Script: {results['script']}")
        
        if 'audio_files' in results:
            print(f"✅ Audio Files: {len(results['audio_files'])} files")
        
        if 'frame_files' in results:
            print(f"✅ Frames: {len(results['frame_files'])} files")
        
        if 'videos' in results:
            print(f"✅ Videos: {len(results['videos'])} files")
            print("\n📹 Generated Videos:")
            for video in results['videos']:
                print(f"   - {video}")
        
        # Show script preview
        print("\n" + "=" * 50)
        runner.show_script_preview(results['script'])
        
    except Exception as e:
        print(f"Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
