import openai
import os
from typing import Optional, Dict, Any
import asyncio
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4"
        
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI response with optional context"""
        try:
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            if context:
                context_str = self._format_context(context)
                messages.insert(1, {"role": "system", "content": f"Context: {context_str}"})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
            
    def _get_system_prompt(self) -> str:
        return """You are STARKAI, an AI assistant inspired by Tony Stark. You are:
        - Confident and decisive in your responses
        - Proactive in identifying and solving problems
        - Witty and charismatic but focused on results
        - Highly technical and innovative
        - Always thinking several steps ahead
        - Integrating information from multiple sources to provide comprehensive solutions"""
        
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for the LLM"""
        formatted = []
        for key, value in context.items():
            formatted.append(f"{key}: {value}")
        return "\n".join(formatted)
