"""
Personality Engine.
Transforms responses based on personality profile and user memory context.
"""
import asyncio
from src.models.memory import UserMemory
from src.models.personality import PersonalityProfile, PersonalityResponse
from src.personality.profiles import PROFILES
from src.llm.client import GroqClient
from src.llm.prompts import GENERIC_RESPONSE_PROMPT


class PersonalityEngine:
    """
    Transforms responses based on personality profile and user memory context.
    
    Key feature: Injects user memory as context to make responses personalized.
    """
    
    def __init__(self, groq_client: GroqClient):
        self.client = groq_client
    
    def _build_memory_context(self, memory: UserMemory) -> str:
        """
        Convert memory to natural language context for prompt injection.
        
        This is the core personalization mechanism - the LLM sees
        relevant user context and can reference it naturally.
        """
        sections = []
        
        if memory.preferences:
            high_conf_prefs = [p for p in memory.preferences if p.confidence >= 0.7][:5]
            if high_conf_prefs:
                prefs = "; ".join(p.description for p in high_conf_prefs)
                sections.append(f"User Preferences: {prefs}")
        
        if memory.emotional_patterns:
            patterns = "; ".join(
                f"{e.pattern} (triggers: {', '.join(e.triggers[:2])})"
                for e in memory.emotional_patterns[:3]
            )
            sections.append(f"Emotional Patterns: {patterns}")
        
        if memory.facts:
            high_importance = [f for f in memory.facts if f.importance in ["high", "medium"]][:5]
            if high_importance:
                facts = "; ".join(f.fact for f in high_importance)
                sections.append(f"Key Facts: {facts}")
        
        return "\n".join(sections) if sections else "No prior context available."
    
    async def generate_response(
        self,
        query: str,
        memory: UserMemory,
        profile_id: str,
    ) -> PersonalityResponse:
        """
        Generate a personalized response using memory and personality.
        
        Args:
            query: User's current message
            memory: Extracted user memory
            profile_id: Which personality to use
            
        Returns:
            PersonalityResponse with the generated text
        """
        profile = PROFILES.get(profile_id)
        if not profile:
            raise ValueError(f"Unknown personality profile: {profile_id}")
        
        memory_context = self._build_memory_context(memory)
        
        system_prompt = f"""{profile.system_prompt}

USER CONTEXT (incorporate naturally, don't force it or be creepy about it):
{memory_context}

STYLE GUIDELINES:
- Formality Level: {profile.formality_level}/10
- Humor Level: {profile.humor_level}/10  
- Empathy Level: {profile.empathy_level}/10

Remember: Use the context to make responses feel personal, but don't explicitly state "I know you like X" - weave it in naturally."""
        
        response = await self.client.generate_response(
            system_prompt=system_prompt,
            user_message=query,
            temperature=profile.temperature,
        )
        
        return PersonalityResponse(
            personality_id=profile_id,
            personality_name=profile.name,
            response=response,
        )
    
    async def generate_generic_response(self, query: str) -> str:
        """
        Generate a generic response without memory or personality.
        Used for before/after comparison.
        """
        return await self.client.generate_response(
            system_prompt=GENERIC_RESPONSE_PROMPT,
            user_message=query,
            temperature=0.7,
        )
    
    async def generate_comparison(
        self,
        query: str,
        memory: UserMemory,
    ) -> dict[str, PersonalityResponse]:
        """
        Generate responses for all personalities for side-by-side comparison.
        
        Uses asyncio.gather for parallel generation.
        """
        tasks = [
            self.generate_response(query, memory, pid)
            for pid in PROFILES.keys()
        ]
        responses = await asyncio.gather(*tasks)
        
        return {r.personality_id: r for r in responses}
