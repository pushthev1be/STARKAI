import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.personality import StarkPersonality

class TestStarkPersonality:
    def setup_method(self):
        self.personality = StarkPersonality()
        
    def test_confidence_filter(self):
        response = "I think this might work"
        filtered = self.personality.apply_personality_filter(response)
        
        assert "I know" in filtered
        assert "definitely" in filtered or "I think" not in filtered
        
    def test_technical_language_enhancement(self):
        response = "We need to fix this error"
        filtered = self.personality.apply_personality_filter(response)
        
        assert "optimize" in filtered or "anomaly" in filtered
        
    def test_contextual_opener(self):
        opener = self.personality.get_contextual_opener("problem_solving")
        
        assert opener in self.personality.response_patterns["problem_solving"]
        
    def test_proactive_suggestions_with_problem_context(self):
        response = "Here's the solution"
        context = {"issue": "performance problem"}
        
        filtered = self.personality.apply_personality_filter(response, context)
        
        assert "what I'd do differently next time" in filtered
