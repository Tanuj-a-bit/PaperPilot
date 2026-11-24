"""Gemini API wrapper with automatic retry & exponential backoff for rate limits."""

import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InternalServerError
from src.config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)


def generate(prompt: str, system_instruction: str = None, max_retries: int = 4) -> str:
    """
    Call Gemini with automatic exponential backoff to handle 429 ResourceExhausted limits.
    """
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=system_instruction,
    )
    
    delay = 5
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                # Sleep and retry
                time.sleep(delay)
                delay *= 2
            else:
                return (
                    "⚠️ Free Tier Gemini API rate limit reached (requests per minute). "
                    "Please wait a few seconds and try again."
                )
        except InternalServerError:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise
        except Exception as e:
            raise e
    return "Rate limit exceeded. Please wait a moment and try again."
