from typing import List, Optional
from pydantic import BaseModel
import re
import json
from ..models.subtask import Subtask
from .clients.gemini_client import GeminiClient  

class SubtaskAIService:
    def __init__(self):
        self.ai_client = GeminiClient()  # Gemini client instance

    def get_subtasks_from_ai(self, main_task_description: str) -> List[Subtask]:
        prompt = self._build_prompt(main_task_description)

        try:
            response = self.ai_client.generate_text(prompt)
            response_text = response.text if hasattr(response, "text") else str(response)
            return self._parse_response_to_subtasks(response_text)
        except Exception as e:
            raise RuntimeError(f"Error generating subtasks from AI: {e}")

    def _build_prompt(self, task_description: str) -> str:
        return (
            "You are a smart and expert project assistant.\n\n"
            f"Given the following task description:\n\"{task_description}\"\n\n"
            "Break it down into 3 to 6 subtasks. For each subtask provide:\n"  
            "- name\n"
            "- description\n"
            "- priority (one of HIGH, MEDIUM, LOW based on its relative importance)\n\n"
            "Return only a JSON array, Output MUST be valid JSON array only, with no additional text or explanation. like this example format:\n"
            "[\n"
            "  {\"name\": \"Design login page\", \"description\": \"Create UI layout for login\", \"priority\": \"HIGH\"},\n"
            "  {\"name\": \"Implement backend auth\", \"description\": \"JWT token generation\", \"priority\": \"MEDIUM\"}\n"
            "]"
        )
    
    def string_to_json(self, json_string):
        try:
            # Parse the string into a JSON object (Python dictionary/list)
            json_object = json.loads(json_string)
            print("Parsed JSON object:", json_object)  # Debugging line
            print("Parsed JSON object: %s", json_object)  # Debug level for detailed info 
            return json_object
        except json.JSONDecodeError as e:
            # Handle invalid JSON format
            print(f"Error decoding JSON: {e}")
            return None

    def _parse_response_to_subtasks(self, response_text: str) :#-> List[Subtask]:
        try:
            
            cleaned_response = re.sub(r"^```json\s*|\s*```$", "", response_text).strip()
            return self.string_to_json(cleaned_response)
        except Exception as e:
            raise ValueError(f"Failed to parse AI response to JSON list of subtasks: {e}")
