import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_engine import LLMEngine

class TestLLMEngine:
    def setup_method(self):
        self.engine = LLMEngine()
        
    @patch('core.llm_engine.openai.OpenAI')
    async def test_generate_response_success(self, mock_openai):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        engine = LLMEngine()
        result = await engine.generate_response("Test prompt")
        
        assert result == "Test response"
        
    async def test_generate_response_with_context(self):
        context = {"system_state": "active", "timestamp": "2024-01-01"}
        
        formatted_context = self.engine._format_context(context)
        
        assert "system_state: active" in formatted_context
        assert "timestamp: 2024-01-01" in formatted_context
        
    def test_system_prompt_contains_stark_traits(self):
        prompt = self.engine._get_system_prompt()
        
        assert "Tony Stark" in prompt
        assert "confident" in prompt.lower()
        assert "proactive" in prompt.lower()
        assert "technical" in prompt.lower()
