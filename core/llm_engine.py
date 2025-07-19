"""
LLM Engine - Handles communication with GPT or local LLM models
Provides unified interface for AI processing with personality integration
"""

import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class LLMEngine:
    """Unified interface for LLM communication"""
    
    def __init__(self, personality=None):
        self.personality = personality
        self.openai_client = None
        self.local_model = None
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from creds.json"""
        config_path = Path(__file__).parent.parent / "config" / "creds.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def initialize(self):
        """Initialize LLM connections"""
        print("Initializing LLM Engine...")
        
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY') or self.config.get('openai', {}).get('api_key')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                print("✓ OpenAI GPT connection established")
            else:
                print("⚠ OpenAI API key not found")
        else:
            print("⚠ OpenAI library not available")
        
        print("✓ LLM Engine initialized")
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate AI response with personality"""
        
        if self.personality:
            prompt = self.personality.apply_personality(prompt, context)
        
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        return self._fallback_response(prompt)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt with personality"""
        base_prompt = "You are STARKAI, an advanced AI assistant."
        
        if self.personality:
            personality_prompt = self.personality.get_system_prompt()
            return f"{base_prompt} {personality_prompt}"
        
        return base_prompt
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when no LLM is available"""
        responses = [
            "I'm processing that request, but my main AI systems are offline.",
            "Let me think about that... My neural networks are currently limited.",
            "That's an interesting question. I'll need to work with reduced capabilities.",
            "I hear you, but I'm running on backup systems right now."
        ]
        
        if any(word in prompt.lower() for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm STARKAI, though I'm running on limited systems right now."
        elif any(word in prompt.lower() for word in ['help', 'what', 'how']):
            return "I'd love to help, but my main AI capabilities are currently offline. Try again later."
        else:
            import random
            return random.choice(responses)
    
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code for issues and improvements"""
        prompt = f"""
        Analyze this {language} code for issues, improvements, and potential fixes:
        
        ```{language}
        {code}
        ```
        
        Provide analysis in JSON format with: issues, suggestions, fixes
        """
        
        response = self.generate_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "issues": ["Could not analyze code properly"],
                "suggestions": ["Manual review recommended"],
                "fixes": []
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "openai_available": self.openai_client is not None,
            "local_model_available": self.local_model is not None,
            "personality_active": self.personality is not None
        }
