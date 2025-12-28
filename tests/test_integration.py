"""
Integration tests for the extraction and personality modules.
These tests hit the Groq API - run sparingly to respect rate limits.

Usage:
    pytest tests/test_integration.py -v --tb=short
    
    # Run only one test (rate-limit friendly):
    pytest tests/test_integration.py::TestMemoryExtraction::test_extract_single_message -v
"""
import pytest
import asyncio
import json
from pathlib import Path

from src.llm.client import GroqClient
from src.extractors.orchestrator import MemoryOrchestrator
from src.extractors.preferences import PreferenceExtractor
from src.extractors.emotions import EmotionalPatternExtractor
from src.extractors.facts import FactExtractor
from src.personality.engine import PersonalityEngine
from src.personality.profiles import PROFILES
from src.models.messages import ChatMessage


# Skip all tests if no API key (CI-friendly)
pytestmark = pytest.mark.skipif(
    not Path("/Users/ioop/Documents/gupshup/.env").exists(),
    reason="No .env file with GROQ_API_KEY"
)


@pytest.fixture(scope="module")
def groq_client():
    """Shared Groq client for all tests in module."""
    return GroqClient()


@pytest.fixture(scope="module")
def sample_messages():
    """Load sample messages once for all tests."""
    data_path = Path(__file__).parent.parent / "data" / "sample_messages.json"
    with open(data_path) as f:
        data = json.load(f)
    return [ChatMessage(**m) for m in data]


@pytest.fixture(scope="module")
def few_messages():
    """Just 3 messages for quick tests (rate-limit friendly)."""
    return [
        ChatMessage(content="I love hiking on weekends. It helps me relax."),
        ChatMessage(content="Work has been stressful lately. Too many deadlines."),
        ChatMessage(content="I work as a software engineer at a startup in Bangalore."),
    ]


class TestGroqClient:
    """Tests for the Groq API client."""
    
    def test_client_initialization(self, groq_client):
        """Test that client initializes with API key."""
        assert groq_client is not None
        assert groq_client.model == "llama-3.3-70b-versatile"
    
    @pytest.mark.asyncio
    async def test_generate_response(self, groq_client):
        """Test basic response generation."""
        response = await groq_client.generate_response(
            system_prompt="You are a helpful assistant. Respond briefly.",
            user_message="Say 'Hello' and nothing else.",
            temperature=0.0,
            max_tokens=10
        )
        assert "Hello" in response or "hello" in response.lower()


class TestMemoryExtraction:
    """Integration tests for memory extraction modules."""
    
    @pytest.mark.asyncio
    async def test_preference_extraction(self, groq_client, few_messages):
        """Test preference extraction from messages."""
        extractor = PreferenceExtractor(groq_client)
        formatted = "\n".join(f"[{i}] {m.content}" for i, m in enumerate(few_messages))
        
        preferences = await extractor.extract(formatted)
        
        assert isinstance(preferences, list)
        # Should find at least the hiking preference
        if preferences:
            assert all(0 <= p.confidence <= 1 for p in preferences)
            assert all(len(p.source_message_ids) > 0 for p in preferences)
    
    @pytest.mark.asyncio
    async def test_emotion_extraction(self, groq_client, few_messages):
        """Test emotional pattern extraction."""
        extractor = EmotionalPatternExtractor(groq_client)
        formatted = "\n".join(f"[{i}] {m.content}" for i, m in enumerate(few_messages))
        
        patterns = await extractor.extract(formatted)
        
        assert isinstance(patterns, list)
        # Should find stress pattern
        if patterns:
            assert all(p.frequency in ["rare", "occasional", "frequent"] for p in patterns)
    
    @pytest.mark.asyncio
    async def test_fact_extraction(self, groq_client, few_messages):
        """Test fact extraction."""
        extractor = FactExtractor(groq_client)
        formatted = "\n".join(f"[{i}] {m.content}" for i, m in enumerate(few_messages))
        
        facts = await extractor.extract(formatted)
        
        assert isinstance(facts, list)
        # Should find the job/location fact
        if facts:
            assert all(f.importance in ["low", "medium", "high"] for f in facts)
    
    @pytest.mark.asyncio
    async def test_orchestrator_parallel_extraction(self, groq_client, few_messages):
        """Test that orchestrator runs extractors in parallel."""
        orchestrator = MemoryOrchestrator(groq_client)
        
        memory = await orchestrator.extract_all(few_messages)
        
        assert memory.message_count == 3
        # At least one type should have results
        total_items = (
            len(memory.preferences) + 
            len(memory.emotional_patterns) + 
            len(memory.facts)
        )
        assert total_items > 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_with_empty_messages(self, groq_client):
        """Test orchestrator handles empty input."""
        orchestrator = MemoryOrchestrator(groq_client)
        
        memory = await orchestrator.extract_all([])
        
        assert memory.message_count == 0
        assert len(memory.preferences) == 0


class TestPersonalityEngine:
    """Integration tests for personality engine."""
    
    @pytest.mark.asyncio
    async def test_generate_response_calm_mentor(self, groq_client, few_messages):
        """Test calm mentor personality response."""
        orchestrator = MemoryOrchestrator(groq_client)
        engine = PersonalityEngine(groq_client)
        
        # First extract memory
        memory = await orchestrator.extract_all(few_messages)
        
        # Then generate response
        response = await engine.generate_response(
            query="I'm feeling overwhelmed with work.",
            memory=memory,
            profile_id="calm-mentor"
        )
        
        assert response.personality_id == "calm-mentor"
        assert len(response.response) > 0
    
    @pytest.mark.asyncio
    async def test_generate_generic_response(self, groq_client):
        """Test generic response (no memory)."""
        engine = PersonalityEngine(groq_client)
        
        response = await engine.generate_generic_response("Hello, how are you?")
        
        assert len(response) > 0
    
    def test_all_profiles_exist(self):
        """Test that all expected profiles are defined."""
        expected = {"calm-mentor", "witty-friend", "therapist"}
        assert set(PROFILES.keys()) == expected
    
    def test_profile_attributes(self):
        """Test that profiles have required attributes."""
        for profile_id, profile in PROFILES.items():
            assert profile.id == profile_id
            assert len(profile.name) > 0
            assert len(profile.system_prompt) > 50
            assert 0 <= profile.temperature <= 1
            assert 1 <= profile.formality_level <= 10
            assert 1 <= profile.humor_level <= 10
            assert 1 <= profile.empathy_level <= 10


# Helper to run async tests
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
