"""
Emotional pattern extractor module.
Identifies recurring emotional patterns, triggers, and frequency.
"""
from src.models.memory import EmotionalPattern, EmotionalPatternList
from src.llm.prompts import EMOTION_EXTRACTION_PROMPT


class EmotionalPatternExtractor:
    """Extracts emotional patterns from formatted conversation history."""
    
    def __init__(self, groq_client):
        self.client = groq_client
    
    async def extract(self, formatted_messages: str) -> list[EmotionalPattern]:
        """
        Extract emotional patterns from formatted messages.
        
        Args:
            formatted_messages: Messages formatted as "[index] content"
            
        Returns:
            List of EmotionalPattern objects
        """
        result = await self.client.extract_structured(
            system_prompt=EMOTION_EXTRACTION_PROMPT,
            user_content=formatted_messages,
            response_model=EmotionalPatternList,
        )
        return result.emotional_patterns
