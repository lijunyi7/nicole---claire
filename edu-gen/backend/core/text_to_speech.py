"""
Text-to-Speech module using OpenAI's TTS API.
Generates audio files for educational script narrations.
"""

from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI
import sys
# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.env_config import get_openai_api_key


class TextToSpeechGenerator:
    """Generates audio files using OpenAI's Text-to-Speech API."""
    
    # Available voices from OpenAI TTS
    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def __init__(self, api_key: str = None, voice: str = "nova"):
        """
        Initialize the TTS generator.
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            voice: Voice to use for TTS (default: "nova")
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            try:
                api_key = get_openai_api_key()
                self.client = OpenAI(api_key=api_key)
            except ValueError as e:
                raise ValueError(f"Failed to initialize OpenAI client: {e}") from e
        
        # Validate voice selection
        if voice not in self.AVAILABLE_VOICES:
            print(f"Warning: Voice '{voice}' not available. Using 'nova' instead.")
            voice = "nova"
        
        self.voice = voice
    
    def generate_audio(self, text: str, output_path: str, voice: str = None) -> str:
        """
        Generate audio file from text using OpenAI TTS.
        
        Args:
            text: Text to convert to speech
            output_path: Path where to save the audio file
            voice: Voice to use (if None, uses instance default)
            
        Returns:
            Path to the generated audio file
            
        Raises:
            Exception: If TTS generation fails
        """
        try:
            # Use provided voice or instance default
            selected_voice = voice or self.voice
            
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate audio using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",  # Using the standard TTS model
                voice=selected_voice,
                input=text,
                response_format="mp3"
            )
            
            # Save the audio file
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"Generated audio: {output_file}")
            return output_file.name
            
        except Exception as e:
            raise RuntimeError(f"TTS generation failed: {e}") from e
    
    def generate_script_audio(self, script_data: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Generate audio files for all narrations in a script.
        
        Args:
            script_data: The script data containing narrations
            output_dir: Directory to save audio files
            
        Returns:
            List of generated audio file paths
        """
        audio_files = []
        output_path = Path(output_dir)
        
        # Generate audio for each section
        sections_to_process = [
            ("intro", "narration", "intro_narration.mp3"),
            ("explanation", "narration", "explanation_narration.mp3"),
            ("practice_mcq", "question", "practice_mcq_question.mp3"),
            ("practice_mcq", "explanation", "practice_mcq_explanation.mp3"),
            ("summary", "narration", "summary_narration.mp3")
        ]
        
        for section, field, filename in sections_to_process:
            if section in script_data and field in script_data[section]:
                text = script_data[section][field]
                if text and text.strip():  # Only process non-empty text
                    audio_path = output_path / filename
                    try:
                        generated_path = self.generate_audio(text, str(audio_path))
                        audio_files.append(generated_path)
                    except RuntimeError as e:
                        print(f"Warning: Failed to generate audio for {section}.{field}: {e}")
        
        return audio_files
    
    def update_script_with_audio(self, script_data: Dict[str, Any], audio_files: List[str]) -> Dict[str, Any]:
        """
        Update script data with audio file paths (basenames only).
        """
        # Build a mapping from filename -> logical key
        audio_mapping = {}
        for audio_file in audio_files:
            filename = Path(audio_file).name  # basename only
            if "intro_narration" in filename:
                audio_mapping["intro_narration"] = filename
            elif "explanation_narration" in filename:
                audio_mapping["explanation_narration"] = filename
            elif "practice_mcq_question" in filename:
                audio_mapping["practice_mcq_question"] = filename
            elif "practice_mcq_explanation" in filename:
                audio_mapping["practice_mcq_explanation"] = filename
            elif "summary_narration" in filename:
                audio_mapping["summary_narration"] = filename

        updated_script = script_data.copy()

        # Add audio basenames to sections for use with /audio/<filename>
        if "intro_narration" in audio_mapping and "intro" in updated_script:
            updated_script["intro"]["audio_narration"] = audio_mapping["intro_narration"]

        if "explanation_narration" in audio_mapping and "explanation" in updated_script:
            updated_script["explanation"]["audio_narration"] = audio_mapping["explanation_narration"]

        if "practice_mcq_question" in audio_mapping and "practice_mcq" in updated_script:
            updated_script["practice_mcq"]["audio_question"] = audio_mapping["practice_mcq_question"]

        if "practice_mcq_explanation" in audio_mapping and "practice_mcq" in updated_script:
            updated_script["practice_mcq"]["audio_explanation"] = audio_mapping["practice_mcq_explanation"]

        if "summary_narration" in audio_mapping and "summary" in updated_script:
            updated_script["summary"]["audio_narration"] = audio_mapping["summary_narration"]

        # Update metadata
        if "metadata" not in updated_script:
            updated_script["metadata"] = {}

        updated_script["metadata"]["audio_generated"] = True
        updated_script["metadata"]["voice_used"] = self.voice
        updated_script["metadata"]["audio_files"] = list(audio_mapping.values())  # basenames

        return updated_script

    
    def get_available_voices(self) -> List[str]:
        """
        Get list of available voices.
        
        Returns:
            List of available voice names
        """
        return self.AVAILABLE_VOICES.copy()
    
    def set_voice(self, voice: str) -> None:
        """
        Set the voice to use for TTS generation.
        
        Args:
            voice: Voice name to use
            
        Raises:
            ValueError: If voice is not available
        """
        if voice not in self.AVAILABLE_VOICES:
            raise ValueError(f"Voice '{voice}' not available. Available voices: {self.AVAILABLE_VOICES}")
        
        self.voice = voice
        print(f"Voice set to: {voice}")


def main():
    """Demo function to test TTS generation."""
    try:
        # Initialize TTS generator
        tts = TextToSpeechGenerator()
        
        print("🎤 OpenAI Text-to-Speech Demo")
        print("=" * 40)
        print(f"Available voices: {tts.get_available_voices()}")
        print(f"Current voice: {tts.voice}")
        
        # Test text
        test_text = "Hello! This is a test of OpenAI's text-to-speech functionality."
        
        # Create output directory
        output_dir = Path(__file__).parent.parent / "outputs" / "audio"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate test audio
        output_file = output_dir / "test_tts.mp3"
        generated_path = tts.generate_audio(test_text, str(output_file))
        
        print(f"✅ Test audio generated: {generated_path}")
        
    except RuntimeError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
