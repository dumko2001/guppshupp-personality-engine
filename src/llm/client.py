"""
Groq client abstraction with JSON mode support and error handling.
"""
import os
import json
from typing import TypeVar, Type
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class GroqClient:
    """
    Async-ready Groq client with structured output support.
    
    Uses Groq's JSON object mode for reliable structured extraction.
    Compatible with llama-3.3-70b-versatile for best performance.
    """
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Set it in .env or pass directly.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
    
    async def extract_structured(
        self,
        system_prompt: str,
        user_content: str,
        response_model: Type[T],
    ) -> T:
        """
        Extract structured data using Groq's JSON object mode.
        
        Args:
            system_prompt: Instructions for the extraction task
            user_content: The content to extract from
            response_model: Pydantic model to validate response
            
        Returns:
            Validated Pydantic model instance
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for consistent extraction
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from Groq API")
        
        parsed = json.loads(content)
        return response_model.model_validate(parsed)
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a natural language response.
        
        Args:
            system_prompt: System instructions and context
            user_message: The user's query
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            Generated response text
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content or ""
