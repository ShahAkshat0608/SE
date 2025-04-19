from google import genai
import re
import logging
import json

# Configure logger
logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        try:
            self.client = genai.Client(api_key="AIzaSyDj0Wf03aSSVKMkmhjg7TJPAHSdQVUDqgQ")
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise RuntimeError(f"Failed to initialize Gemini client: {str(e)}")

    def generate_text(self, prompt):
        if prompt is None or prompt.strip() == "":
            logger.error("Empty prompt provided to Gemini client")
            raise ValueError("Prompt cannot be empty")
            
        logger.info("Sending request to Gemini API")
        
        try:
            # Call Gemini API for text generation
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", contents=prompt
            )
            
            if not hasattr(response, 'text'):
                logger.error("Unexpected response format from Gemini API")
                return json.dumps([{"name": "Error", "description": "AI service returned an invalid response format", "priority": "HIGH"}])
                
            text_json_response = response.text.strip()
            logger.info("Successfully received response from Gemini API")
            
            return text_json_response
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
            # Return a fallback response instead of raising to prevent 500 errors
            return json.dumps([
                {"name": "Review task requirements", "description": "Analyze the main task requirements and break it down", "priority": "HIGH"},
                {"name": "Create implementation plan", "description": "Develop a plan for implementing the required functionality", "priority": "MEDIUM"},
                {"name": "Test implementation", "description": "Ensure the implementation works as expected", "priority": "MEDIUM"}
            ])
        