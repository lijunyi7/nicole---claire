"""
Core script generation module using OpenAI API.
Generates educational scripts in JSON format following edu_script_v0.1 schema
"""

import json
import os
from typing import Dict, Any
from openai import OpenAI
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.env_config import get_openai_api_key


class ScriptGenerator:
    """Generates educational scripts using OpenAI API."""
    
    def __init__(self, api_key: str = None, generate_audio: bool = False):
        """Initialize the script generator with OpenAI API key."""
        self.generate_audio = generate_audio
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            try:
                api_key = get_openai_api_key()
                self.client = OpenAI(api_key=api_key)
            except ValueError as e:
                raise ValueError(f"Failed to initialize OpenAI client: {e}")
    
    def generate_script(self, topic: str, prompt_template: str) -> Dict[str, Any]:
        """
        Generate an educational script for the given topic.
        
        Args:
            topic: The educational topic (e.g., "十以内减法：9 - 4")
            prompt_template: The prompt template to use
            
        Returns:
            Dictionary containing the generated script
            
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

            # --- Optional Audio Generation ---
            if self.generate_audio:
                audio_filename = self._generate_audio(script_data, topic)
                script_data["metadata"]["audio_file"] = audio_filename
            
            return script_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
    
    def _generate_audio(self, script_data: Dict[str, Any], topic: str) -> str:
        """Generate TTS audio for the full narration and save as MP3."""
        audio_dir = Path(__file__).parent.parent / "outputs" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Collect narration text
        full_text = " ".join([
            script_data.get("intro", {}).get("narration", ""),
            script_data.get("explanation", {}).get("narration", ""),
            script_data.get("practice_mcq", {}).get("question", ""),
            script_data.get("summary", {}).get("narration", "")
        ])

        audio_filename = f"{topic.replace(' ', '_')}.mp3"
        audio_path = audio_dir / audio_filename

        tts = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=full_text
        )

        with open(audio_path, "wb") as f:
            f.write(tts.read())

        return audio_filename
    
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
