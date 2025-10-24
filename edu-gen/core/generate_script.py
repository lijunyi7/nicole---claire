"""
Core script generation module using OpenAI API.
Generates educational scripts in JSON format following edu_script_v0.1 schema.
"""

import json
import os
from typing import Dict, Any
from openai import OpenAI
from pathlib import Path


class ScriptGenerator:
    """Generates educational scripts using OpenAI API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the script generator with OpenAI API key."""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
    
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
            script_data = json.loads(script_content)
            
            # Add metadata
            script_data["metadata"] = {
                "version": "0.1",
                "language": "en-US", 
                "tone": "elementary",
                "topic": topic,
                "duration_estimate": self._estimate_duration(script_data)
            }
            
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
    import sys
    
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
        generator = ScriptGenerator()
        script_data = generator.generate_script(topic, prompt_template)
        
        # Save to outputs directory
        output_dir = Path(__file__).parent.parent / "outputs" / "scripts"
        output_file = output_dir / f"{topic.replace('：', '_').replace(' ', '_')}.json"
        generator.save_script(script_data, str(output_file))
        
        print("Script generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
