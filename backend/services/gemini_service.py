import os
import google.generativeai as genai

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest') # Using a general model, can be made configurable

    def generate_content(self, prompt: str):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Implement more specific error handling based on genai exceptions
            print(f"Error generating content from Gemini API: {e}")
            return None

gemini_service = GeminiService()

if __name__ == "__main__":
    # This block is for testing purposes only and should not be run in production
    # To test, set GEMINI_API_KEY in your environment or a .env file
    # and run this file directly: python backend/services/gemini_service.py
    try:
        # Example usage:
        test_prompt = "What is the capital of France?"
        response_text = gemini_service.generate_content(test_prompt)
        if response_text:
            print(f"Gemini API Response: {response_text}")
        else:
            print("Failed to get response from Gemini API.")
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")