"""
Edge case tests for robustness verification.
These test boundary conditions and error handling.
"""
import pytest
from src.models.memory import UserMemory, Preference, EmotionalPattern, Fact
from src.models.messages import ChatMessage


class TestEdgeCases:
    """Edge case tests for models."""
    
    def test_empty_user_memory(self):
        """Test empty memory initialization."""
        memory = UserMemory(message_count=0)
        assert len(memory.preferences) == 0
        assert len(memory.emotional_patterns) == 0
        assert len(memory.facts) == 0
        assert memory.extraction_errors == []
    
    def test_preference_with_empty_source_ids(self):
        """Source message IDs can be empty list."""
        pref = Preference(
            category="interests",
            description="Test",
            confidence=0.5,
            source_message_ids=[],
            evidence="inferred"
        )
        assert pref.source_message_ids == []
    
    def test_emotional_pattern_with_empty_triggers(self):
        """Triggers can be empty list."""
        pattern = EmotionalPattern(
            pattern="general sadness",
            triggers=[],
            frequency="rare",
            emotional_range=["sad"],
            source_message_ids=[0]
        )
        assert pattern.triggers == []
    
    def test_message_with_unicode(self):
        """Messages can contain Unicode characters."""
        msg = ChatMessage(content="日本語 and emojis 🎉 работает")
        assert "日本語" in msg.content
        assert "🎉" in msg.content
    
    def test_message_with_special_html(self):
        """Messages can contain HTML-like content (stored as-is)."""
        msg = ChatMessage(content="<script>alert(1)</script>")
        assert "<script>" in msg.content
    
    def test_very_long_message(self):
        """Messages can be very long."""
        long_content = "word " * 1000
        msg = ChatMessage(content=long_content)
        assert len(msg.content) > 4000
    
    def test_preference_boundary_confidence(self):
        """Test confidence at exact boundaries."""
        # Exactly 0
        p1 = Preference(
            category="values", description="t", confidence=0.0,
            source_message_ids=[0], evidence="t"
        )
        assert p1.confidence == 0.0
        
        # Exactly 1
        p2 = Preference(
            category="values", description="t", confidence=1.0,
            source_message_ids=[0], evidence="t"
        )
        assert p2.confidence == 1.0
    
    def test_memory_with_errors(self):
        """Memory can track extraction errors."""
        memory = UserMemory(
            message_count=10,
            extraction_errors=["API timeout", "Parse error"]
        )
        assert len(memory.extraction_errors) == 2
    
    def test_all_fact_categories(self):
        """All fact categories are valid."""
        for cat in ["personal", "professional", "relational", "temporal"]:
            fact = Fact(
                category=cat,
                fact="test",
                importance="medium",
                confidence=0.5,
                source_message_ids=[0]
            )
            assert fact.category == cat
    
    def test_all_preference_categories(self):
        """All preference categories are valid."""
        for cat in ["communication", "interests", "lifestyle", "values"]:
            pref = Preference(
                category=cat,
                description="test",
                confidence=0.5,
                source_message_ids=[0],
                evidence="test"
            )
            assert pref.category == cat


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
