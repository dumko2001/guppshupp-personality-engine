"""
Fact extractor module.
Extracts factual information about the user with importance ranking.
"""
from src.models.memory import Fact, FactList
from src.llm.prompts import FACT_EXTRACTION_PROMPT


class FactExtractor:
    """Extracts facts from formatted conversation history."""
    
    def __init__(self, groq_client):
        self.client = groq_client
    
    async def extract(self, formatted_messages: str) -> list[Fact]:
        """
        Extract facts from formatted messages.
        
        Args:
            formatted_messages: Messages formatted as "[index] content"
            
        Returns:
            List of Fact objects with importance ranking
        """
        result = await self.client.extract_structured(
            system_prompt=FACT_EXTRACTION_PROMPT,
            user_content=formatted_messages,
            response_model=FactList,
        )
        return result.facts
