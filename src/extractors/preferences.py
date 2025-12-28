"""
Preference extractor module.
Extracts user preferences with confidence scoring and source attribution.
"""
from src.models.memory import Preference, PreferenceList
from src.llm.prompts import PREFERENCE_EXTRACTION_PROMPT


class PreferenceExtractor:
    """Extracts user preferences from formatted conversation history."""
    
    def __init__(self, groq_client):
        self.client = groq_client
    
    async def extract(self, formatted_messages: str) -> list[Preference]:
        """
        Extract preferences from formatted messages.
        
        Args:
            formatted_messages: Messages formatted as "[index] content"
            
        Returns:
            List of Preference objects with confidence scores
        """
        result = await self.client.extract_structured(
            system_prompt=PREFERENCE_EXTRACTION_PROMPT,
            user_content=formatted_messages,
            response_model=PreferenceList,
        )
        return result.preferences
