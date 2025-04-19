from typing import List, Optional
from pydantic import BaseModel
import re
import json
import logging
from ..models.subtask import Subtask
from .clients.gemini_client import GeminiClient  

# Configure logger
logger = logging.getLogger(__name__)

class SubtaskAIService:
    def __init__(self):
        self.ai_client = GeminiClient()  # Gemini client instance

    def get_subtasks_from_ai(self, main_task_description: str) -> List[Subtask]:
        prompt = self._build_prompt(main_task_description)
        logger.info(f"Generating subtasks for task description: {main_task_description}")

        try:
            response = self.ai_client.generate_text(prompt)
            logger.info("Successfully received response from AI service")
            response_text = response if isinstance(response, str) else (response.text if hasattr(response, "text") else str(response))
            
            # Log the raw response for debugging
            logger.debug(f"Raw AI response: {response_text}")
            
            subtasks = self._parse_response_to_subtasks(response_text)
            logger.info(f"Successfully parsed {len(subtasks)} subtasks from AI response")
            return subtasks
        except Exception as e:
            logger.error(f"Error generating subtasks from AI: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error generating subtasks from AI: {str(e)}")

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
            logger.debug(f"Attempting to parse JSON: {json_string}")
            json_object = json.loads(json_string)
            logger.info("Successfully parsed JSON object")
            return json_object
        except json.JSONDecodeError as e:
            # Handle invalid JSON format
            logger.error(f"Error decoding JSON: {str(e)}")
            logger.debug(f"Invalid JSON string: {json_string}")
            raise ValueError(f"Failed to parse AI response: {str(e)}. Response was: {json_string[:100]}...")

    def _parse_response_to_subtasks(self, response_text: str) :#-> List[Subtask]:
        try:
            # Handle potential JSON code blocks in markdown format
            cleaned_response = re.sub(r"^```json\s*|\s*```$", "", response_text).strip()
            
            # Try to find a JSON array if the response contains other text
            match = re.search(r'\[\s*{.*}\s*\]', cleaned_response, re.DOTALL)
            if match:
                cleaned_response = match.group(0)
                
            logger.debug(f"Cleaned response for parsing: {cleaned_response}")
            return self.string_to_json(cleaned_response)
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to parse AI response to JSON list of subtasks: {str(e)}")
