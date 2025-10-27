"""
Environment configuration module for loading API keys from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """
    Load environment variables from .env file.
    Looks for .env file in the project root directory.
    """
    # Get the project root directory (parent of this file's directory)
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment variables from: {env_file}")
    else:
        print(f"No .env file found at: {env_file}")
        print("   Using system environment variables only")


def get_openai_api_key() -> str:
    """
    Get OpenAI API key from environment variables.
    
    Returns:
        OpenAI API key string
        
    Raises:
        ValueError: If API key is not found
    """
    # Load environment variables first
    load_environment()
    
    # Try to get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file or environment variables.\n"
            "Create a .env file in the project root with:\n"
            "OPENAI_API_KEY=your_api_key_here"
        )
    
    return api_key


def check_environment_setup() -> bool:
    """
    Check if the environment is properly set up.
    
    Returns:
        True if environment is properly configured, False otherwise
    """
    try:
        get_openai_api_key()
        return True
    except ValueError:
        return False


def main():
    """Demo function to test environment loading."""
    print("🔧 Environment Configuration Check")
    print("=" * 40)
    
    # Load environment
    load_environment()
    
    # Check if API key is available
    if check_environment_setup():
        print("Environment is properly configured")
        print("OpenAI API key is available")
    else:
        print("Environment configuration issues found")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add: OPENAI_API_KEY=your_api_key_here")
        print("3. Or set the environment variable: export OPENAI_API_KEY=your_api_key_here")


if __name__ == "__main__":
    main()
