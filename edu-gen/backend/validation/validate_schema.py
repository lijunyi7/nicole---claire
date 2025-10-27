"""
Schema validation module for edu_script_v0.1.
Validates generated scripts against the JSON schema.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, List, Tuple


class SchemaValidator:
    """Validates educational scripts against the edu_script_v0.1 schema."""
    
    def __init__(self, schema_path: str = None):
        """
        Initialize the validator with schema file.
        
        Args:
            schema_path: Path to the JSON schema file
        """
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "schema" / "edu_script_v0.1.json"
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
    
    def validate_script(self, script_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a script against the schema.
        
        Args:
            script_data: The script data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            jsonschema.validate(script_data, self.schema)
            return True, []
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return False, errors
        except jsonschema.SchemaError as e:
            errors.append(f"Schema error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error during validation: {e}")
            return False, errors
    
    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a script file against the schema.
        
        Args:
            file_path: Path to the JSON script file
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
            return self.validate_script(script_data)
        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Error reading file: {e}"]
    
    def get_validation_report(self, script_data: Dict[str, Any]) -> str:
        """
        Generate a detailed validation report.
        
        Args:
            script_data: The script data to validate
            
        Returns:
            Detailed validation report string
        """
        is_valid, errors = self.validate_script(script_data)
        
        report = []
        report.append("=" * 50)
        report.append("EDUCATIONAL SCRIPT VALIDATION REPORT")
        report.append("=" * 50)
        
        if is_valid:
            report.append("✅ VALIDATION PASSED")
            report.append("The script conforms to edu_script_v0.1 schema.")
        else:
            report.append("❌ VALIDATION FAILED")
            report.append("The following errors were found:")
            for i, error in enumerate(errors, 1):
                report.append(f"  {i}. {error}")
        
        # Additional checks
        report.append("\n" + "-" * 30)
        report.append("ADDITIONAL CHECKS")
        report.append("-" * 30)
        
        # Check required sections
        required_sections = ["intro", "explanation", "practice_mcq", "summary"]
        for section in required_sections:
            if section in script_data:
                report.append(f"✅ {section} section present")
            else:
                report.append(f"❌ {section} section missing")
        
        # Check metadata
        if "metadata" in script_data:
            metadata = script_data["metadata"]
            if metadata.get("language") == "en-US":
                report.append("✅ Language set to English (en-US)")
            else:
                report.append("❌ Language not set to English")
            
            if metadata.get("tone") == "elementary":
                report.append("✅ Tone set to elementary")
            else:
                report.append("❌ Tone not set to elementary")
        else:
            report.append("❌ Metadata section missing")
        
        # Check practice MCQ structure
        if "practice_mcq" in script_data:
            mcq = script_data["practice_mcq"]
            if "options" in mcq and len(mcq["options"]) >= 2:
                report.append("✅ MCQ has sufficient options")
            else:
                report.append("❌ MCQ options insufficient")
            
            if "correct_answer" in mcq and isinstance(mcq["correct_answer"], int):
                report.append("✅ MCQ has valid correct answer index")
            else:
                report.append("❌ MCQ correct answer invalid")
        
        return "\n".join(report)


def main():
    """Demo function to test schema validation."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python validate_schema.py <script_file>")
        print("Example: python validate_schema.py outputs/scripts/example.json")
        sys.exit(1)
    
    script_file = sys.argv[1]
    
    try:
        validator = SchemaValidator()
        is_valid, errors = validator.validate_file(script_file)
        
        if is_valid:
            print("✅ Script validation passed!")
        else:
            print("❌ Script validation failed!")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
