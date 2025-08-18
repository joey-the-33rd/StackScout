"""Base AI generator class for all document generation."""
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from pydantic import BaseModel

class BaseAIGenerator:
    """Base class for all AI-powered document generators."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI generator with Google Gemini client."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_content(self, prompt: str, context: Dict[str, Any], max_tokens: int = 1000) -> str:
        """Generate content using Google Gemini."""
        try:
            # Convert max_tokens to character limit (rough approximation)
            max_chars = min(max_tokens * 4, 4000)
            
            # Create the full prompt with system context
            full_prompt = f"{self.get_system_prompt()}\n\nUser Request: {prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            return response.text.strip()
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI model."""
        return "You are a professional career consultant helping job seekers create compelling application documents."
    
    def clean_text(self, text: str) -> str:
        """Clean and format generated text."""
        if not text:
            return ""
        # Remove extra whitespace and normalize formatting
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
