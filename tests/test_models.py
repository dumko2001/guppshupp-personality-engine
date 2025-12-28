"""
Unit tests for the memory extraction models and extractors.
Tests Pydantic validation without hitting the API (rate-limit friendly).
"""
import pytest
from datetime import datetime
from src.models.memory import (
    Preference, PreferenceList,
    EmotionalPattern, EmotionalPatternList,
    Fact, FactList,
    UserMemory
)
from src.models.messages import ChatMessage, ConversationHistory
from src.models.personality import PersonalityProfile, PersonalityResponse


class TestChatMessageModel:
    """Tests for ChatMessage Pydantic model."""
    
    def test_create_user_message(self):
        msg = ChatMessage(role="user", content="Hello, how are you?")
        assert msg.role == "user"
        assert msg.content == "Hello, how are you?"
        assert msg.timestamp is None
    
    def test_create_message_with_timestamp(self):
        now = datetime.utcnow()
        msg = ChatMessage(role="assistant", content="I'm fine!", timestamp=now)
        assert msg.timestamp == now
    
    def test_default_role_is_user(self):
        msg = ChatMessage(content="Test message")
        assert msg.role == "user"


class TestPreferenceModel:
    """Tests for Preference Pydantic model with confidence scoring."""
    
    def test_valid_preference(self):
        pref = Preference(
            category="interests",
            description="Enjoys hiking",
            confidence=0.85,
            source_message_ids=[2, 5, 10],
            evidence="User said 'I love hiking on weekends'"
        )
        assert pref.category == "interests"
        assert pref.confidence == 0.85
        assert len(pref.source_message_ids) == 3
    
    def test_confidence_range_validation(self):
        # Valid: exactly 0
        pref = Preference(
            category="lifestyle",
            description="Test",
            confidence=0.0,
            source_message_ids=[1],
            evidence="test"
        )
        assert pref.confidence == 0.0
        
        # Valid: exactly 1
        pref = Preference(
            category="lifestyle",
            description="Test",
            confidence=1.0,
            source_message_ids=[1],
            evidence="test"
        )
        assert pref.confidence == 1.0
    
    def test_invalid_confidence_raises_error(self):
        with pytest.raises(ValueError):
            Preference(
                category="interests",
                description="Test",
                confidence=1.5,  # Invalid: > 1
                source_message_ids=[1],
                evidence="test"
            )
    
    def test_invalid_category_raises_error(self):
        with pytest.raises(ValueError):
            Preference(
                category="invalid_category",  # Not in Literal
                description="Test",
                confidence=0.5,
                source_message_ids=[1],
                evidence="test"
            )


class TestEmotionalPatternModel:
    """Tests for EmotionalPattern Pydantic model."""
    
    def test_valid_emotional_pattern(self):
        pattern = EmotionalPattern(
            pattern="becomes anxious about deadlines",
            triggers=["deadlines", "boss expectations"],
            frequency="frequent",
            emotional_range=["anxious", "stressed"],
            source_message_ids=[0, 7, 13]
        )
        assert pattern.frequency == "frequent"
        assert "deadlines" in pattern.triggers
    
    def test_invalid_frequency_raises_error(self):
        with pytest.raises(ValueError):
            EmotionalPattern(
                pattern="test",
                triggers=["test"],
                frequency="always",  # Invalid: not in Literal
                emotional_range=["happy"],
                source_message_ids=[1]
            )


class TestFactModel:
    """Tests for Fact Pydantic model with importance ranking."""
    
    def test_valid_fact(self):
        fact = Fact(
            category="professional",
            fact="Works at a startup",
            importance="high",
            confidence=0.95,
            source_message_ids=[4, 18]
        )
        assert fact.importance == "high"
        assert fact.confidence == 0.95
    
    def test_all_importance_levels(self):
        for importance in ["low", "medium", "high"]:
            fact = Fact(
                category="personal",
                fact="Test fact",
                importance=importance,
                confidence=0.5,
                source_message_ids=[1]
            )
            assert fact.importance == importance


class TestUserMemoryModel:
    """Tests for the complete UserMemory model."""
    
    def test_empty_memory(self):
        memory = UserMemory(message_count=0)
        assert len(memory.preferences) == 0
        assert len(memory.emotional_patterns) == 0
        assert len(memory.facts) == 0
        assert memory.message_count == 0
    
    def test_memory_with_all_components(self):
        memory = UserMemory(
            preferences=[
                Preference(
                    category="interests",
                    description="Hiking",
                    confidence=0.9,
                    source_message_ids=[2],
                    evidence="loves hiking"
                )
            ],
            emotional_patterns=[
                EmotionalPattern(
                    pattern="work stress",
                    triggers=["deadlines"],
                    frequency="frequent",
                    emotional_range=["stressed"],
                    source_message_ids=[0]
                )
            ],
            facts=[
                Fact(
                    category="professional",
                    fact="Works at startup",
                    importance="high",
                    confidence=0.95,
                    source_message_ids=[4]
                )
            ],
            message_count=30
        )
        assert len(memory.preferences) == 1
        assert len(memory.emotional_patterns) == 1
        assert len(memory.facts) == 1
        assert memory.message_count == 30
    
    def test_memory_serialization(self):
        """Test that memory can be serialized to JSON."""
        memory = UserMemory(
            preferences=[
                Preference(
                    category="communication",
                    description="Prefers direct communication",
                    confidence=0.85,
                    source_message_ids=[8],
                    evidence="can't stand passive-aggressive"
                )
            ],
            message_count=10
        )
        json_data = memory.model_dump(mode="json")
        assert "preferences" in json_data
        assert json_data["message_count"] == 10


class TestPersonalityModels:
    """Tests for personality-related models."""
    
    def test_personality_profile(self):
        profile = PersonalityProfile(
            id="test-profile",
            name="Test Profile",
            description="A test profile",
            system_prompt="You are a test assistant.",
            temperature=0.7,
            formality_level=5,
            humor_level=3,
            empathy_level=8
        )
        assert profile.temperature == 0.7
        assert 1 <= profile.formality_level <= 10
    
    def test_personality_response(self):
        response = PersonalityResponse(
            personality_id="calm-mentor",
            personality_name="Calm Mentor",
            response="This is a thoughtful response."
        )
        assert response.personality_id == "calm-mentor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
