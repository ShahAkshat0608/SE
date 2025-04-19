from google import genai
import re

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key="AIzaSyDj0Wf03aSSVKMkmhjg7TJPAHSdQVUDqgQ")

    def generate_text(self, prompt):
        if prompt is None:
            raise ValueError("Prompt cannot be empty")
            
        # print("Given promt to gemini:")
        #print(code_snippet)  # Log the given code

        # Call Gemini API for refactoring suggestion
        response = self.client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        text_json_response = response.text.strip()

        # Log the output (received code from AI)
        # print("Received from AI): ", text_json_response) 

        return text_json_response
        