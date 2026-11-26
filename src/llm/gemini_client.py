"""Gemini API wrapper with automatic fallback models and exponential backoff."""

import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, NotFound, InternalServerError
from src.config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

# Fallback sequence if Google deprecates or rate-limits a specific sub-model
FALLBACK_MODELS = [GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.5-flash"]

def generate(prompt: str, system_instruction: str = None, max_retries: int = 3) -> str:
    """
    Call Gemini with automatic model fallback and exponential retry backoff.
    """
    last_error = None
    
    for model_name in dict.fromkeys(FALLBACK_MODELS):  # preserve order without duplicates
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_instruction,
        )
        delay = 4
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                return response.text
            except NotFound:
                # Model name retired or unavailable -> immediately switch to next fallback
                break
            except ResourceExhausted:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    last_error = "Rate limit reached. Please wait a moment and try again."
            except InternalServerError:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    last_error = "Gemini server busy. Please try again."
            except Exception as e:
                last_error = str(e)
                break
                
    if last_error:
        return f"Service response: {last_error}"
    return "Unable to process request at this time. Please retry in a few moments."
