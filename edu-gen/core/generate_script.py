"""
Core script generation module using OpenAI API.
Generates educational scripts in JSON format following edu_script_v0.1 schema
"""

import json
from typing import Dict, Any
from openai import OpenAI
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.env_config import get_openai_api_key
from core.text_to_speech import TextToSpeechGenerator


class ScriptGenerator:
    """Generates educational scripts using OpenAI API."""
    
    def __init__(self, api_key: str = None, generate_audio: bool = True, voice: str = None):
        """
        Initialize the script generator with OpenAI API key.
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            generate_audio: Whether to generate audio files for narrations
            voice: Voice to use for TTS (if None, uses default)
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            try:
                api_key = get_openai_api_key()
                self.client = OpenAI(api_key=api_key)
            except ValueError as e:
                raise ValueError(f"Failed to initialize OpenAI client: {e}")
        
        self.generate_audio = generate_audio
        self.tts_generator = TextToSpeechGenerator(api_key=api_key, voice=voice) if generate_audio else None
    
    def generate_script(self, topic: str, prompt_template: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Generate an educational script for the given topic.
        
        Args:
            topic: The educational topic (e.g., "十以内减法：9 - 4")
            prompt_template: The prompt template to use
            output_dir: Directory to save audio files (if generating audio)
            
        Returns:
            Dictionary containing the generated script with optional audio files
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            # Format the prompt with the topic
            formatted_prompt = prompt_template.format(topic=topic)
            
            # Call OpenAI API with JSON response format
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior educational content generation expert, specializing in creating teaching scripts for elementary students. Please strictly follow the edu_script_v0.1 schema to generate JSON format educational content."
                    },
                    {
                        "role": "user", 
                        "content": formatted_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the JSON response
            script_content = response.choices[0].message.content
            print(f"Debug: Raw OpenAI response: {script_content[:200]}...")  # Show first 200 chars
            raw_data = json.loads(script_content)
            
            # Handle nested structure - extract content if wrapped in edu_script_v0.1
            if "edu_script_v0.1" in raw_data:
                script_data = raw_data["edu_script_v0.1"]
                # If content is nested, extract it
                if "content" in script_data:
                    script_data = script_data["content"]
            else:
                script_data = raw_data
            
            # Add metadata
            script_data["metadata"] = {
                "version": "0.1",
                "language": "en-US", 
                "tone": "elementary",
                "topic": topic,
                "duration_estimate": self._estimate_duration(script_data)
            }
            
            # Generate audio files if requested
            if self.generate_audio and self.tts_generator and output_dir:
                try:
                    print("Generating audio files...")
                    audio_files = self.tts_generator.generate_script_audio(script_data, output_dir)
                    script_data = self.tts_generator.update_script_with_audio(script_data, audio_files)
                    print(f"Generated {len(audio_files)} audio files")
                except Exception as e:
                    print(f"Warning: Audio generation failed: {e}")
                    print("Continuing with text-only script...")
            
            return script_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
    
    def _estimate_duration(self, script_data: Dict[str, Any]) -> float:
        """Estimate the duration of the script in seconds."""
        total_text = ""
        
        # Collect all narration text
        for section in ["intro", "explanation", "practice_mcq", "summary"]:
            if section in script_data:
                if "narration" in script_data[section]:
                    total_text += script_data[section]["narration"]
                if section == "practice_mcq" and "question" in script_data[section]:
                    total_text += script_data[section]["question"]
                if section == "practice_mcq" and "explanation" in script_data[section]:
                    total_text += script_data[section]["explanation"]
        
        # Estimate ~4 words per second for English speech
        word_count = len(total_text.split())
        estimated_duration = word_count / 4.0
        return round(estimated_duration, 1)
    
    def save_script(self, script_data: Dict[str, Any], output_path: str) -> None:
        """
        Save the script to a JSON file.
        
        Args:
            script_data: The script data to save
            output_path: Path to save the JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        print(f"Script saved to: {output_file}")


def main():
    """Demo function to test script generation."""
    
    if len(sys.argv) != 2:
        print("Usage: python generate_script.py <topic>")
        print("Example: python generate_script.py '十以内减法：9 - 4'")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    # Load prompt template
    template_path = Path(__file__).parent.parent / "prompts" / "prompt_template_math.txt"
    with open(template_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    try:
        # Create output directories
        scripts_dir = Path(__file__).parent.parent / "outputs" / "scripts"
        audio_dir = Path(__file__).parent.parent / "outputs" / "audio"
        
        # Initialize generator with audio generation enabled
        generator = ScriptGenerator(generate_audio=True)
        
        # Generate script with audio
        script_data = generator.generate_script(topic, prompt_template, str(audio_dir))
        
        # Save script to outputs directory
        output_file = scripts_dir / f"{topic.replace('：', '_').replace(' ', '_')}.json"
        generator.save_script(script_data, str(output_file))
        
        print("Script generation completed successfully!")
        if generator.generate_audio:
            print(f"Audio files saved to: {audio_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
