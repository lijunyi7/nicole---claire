# Educational Script Generator

A minimal Python project that converts educational topics into structured JSON teaching scripts.

## Features

- 🎯 **Topic to Script**: Convert educational topics into structured JSON scripts
- 📋 **Schema Validation**: Ensures all scripts conform to edu_script_v0.1 schema
- 🔧 **Modular Design**: Clean separation of concerns with testable components
- 🔑 **Environment Configuration**: Easy API key management with .env files

## Project Structure

```
edu-gen/
├─ schema/edu_script_v0.1.json     # JSON schema definition
├─ core/generate_script.py          # OpenAI script generation
├─ validation/validate_schema.py   # Schema validation
├─ config/env_config.py            # Environment configuration
├─ tools/demo_runner.py            # Complete workflow runner
├─ prompts/prompt_template_math.txt # Math topic prompt template
├─ outputs/scripts/                # Generated JSON scripts
├─ .env.example                    # Environment variables template
├─ requirements.txt                # Python dependencies
└─ README.md                       # This file
```

## Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## Usage

### Quick Start (Complete Workflow)

Run the complete workflow from topic to audio:

```bash
python tools/demo_runner.py "Subtraction within 10: 9 - 4"
```

This will:
1. Generate a JSON script using OpenAI GPT-4o-mini
2. Validate the script against the schema
3. Save the script to `outputs/scripts/` directory

### Individual Components

#### 1. Generate Script Only
```bash
python core/generate_script.py "Subtraction within 10: 9 - 4"
```

#### 2. Validate Script
```bash
python validation/validate_schema.py outputs/scripts/Subtraction_within_10_9_-_4.json
```

#### 3. Check Environment Setup
```bash
python config/env_config.py
```

## Schema Format

The generated scripts follow the `edu_script_v0.1` schema with these sections:

- **intro**: Warm introduction to the topic
- **explanation**: Detailed explanation of concepts
- **practice_mcq**: Multiple choice question with options
- **summary**: Conclusion and key takeaways

Each script includes metadata with language (en-US), tone (elementary), and duration estimates.

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for OpenAI API access
- `OUTPUT_DIR`: Optional custom output directory

### Customization

- **Prompt Templates**: Edit `prompts/prompt_template_math.txt` for different subject areas
- **Audio Settings**: Modify gap duration and voice in `tts/synthesize_audio.py`
- **Schema**: Update `schema/edu_script_v0.1.json` for different script formats

## Example Output

### Generated Script Structure
```json
{
  "metadata": {
    "version": "0.1",
    "language": "en-US",
    "tone": "elementary",
    "topic": "Subtraction within 10: 9 - 4",
    "duration_estimate": 45.2
  },
  "intro": {
    "title": "Welcome to Subtraction",
    "narration": "Today we're going to learn subtraction within 10..."
  },
  "explanation": {
    "title": "Subtraction Concepts",
    "narration": "Subtraction means taking away one number from another..."
  },
  "practice_mcq": {
    "title": "Practice Time",
    "question": "What is 9 - 4?",
    "options": ["3", "4", "5", "6"],
    "correct_answer": 2,
    "explanation": "9 minus 4 equals 5, because when we take away 4 from 9, we have 5 left."
  },
  "summary": {
    "title": "Summary",
    "narration": "Today we learned about subtraction within 10..."
  }
}
```

### Audio Output
- **Format**: JSON scripts ready for TTS processing
- **Structure**: Well-organized sections for easy audio generation
- **Quality**: High-quality educational content

## Error Handling

The system includes robust error handling for:
- Invalid API responses
- Schema validation failures
- Audio synthesis errors
- File I/O operations

All errors are logged with clear messages to help with debugging.

## Requirements

- Python 3.10+
- OpenAI API key
- Internet connection for API calls

## Dependencies

- `openai>=1.0.0`: OpenAI API client
- `jsonschema>=4.0.0`: JSON schema validation
- `python-dotenv>=1.0.0`: Environment variable loading

## License

This project is for educational purposes. Please ensure you have proper OpenAI API access and follow their usage policies.
