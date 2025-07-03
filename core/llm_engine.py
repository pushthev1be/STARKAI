"""
LLM Engine Module
Handles communication with GPT or local language models
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Response from LLM with metadata"""
    content: str
    model: str
    tokens_used: int
    success: bool
    error: Optional[str] = None

class LLMEngine:
    """Handles LLM communication with fallback options"""
    
    def __init__(self, config_path: str = "config/creds.json"):
        self.config_path = config_path
        self.api_keys = self._load_credentials()
        self.default_model = "gpt-3.5-turbo"
        self.local_model_url = "http://localhost:11434"  # Ollama default
        
    def _load_credentials(self) -> Dict[str, Any]:
        """Load API credentials from config file"""
        try:
            with open(self.config_path, 'r') as f:
                creds = json.load(f)
            return creds
        except FileNotFoundError:
            return {}
    
    def _get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key from environment or config"""
        return os.getenv('OPENAI_API_KEY') or self.api_keys.get('openai', {}).get('api_key')
    
    def query_openai(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> LLMResponse:
        """Query OpenAI GPT models"""
        api_key = self._get_openai_key()
        if not api_key:
            return LLMResponse("", "", 0, False, "No OpenAI API key found")
        
        model = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                tokens = data['usage']['total_tokens']
                return LLMResponse(content, model, tokens, True)
            else:
                return LLMResponse("", model, 0, False, f"API Error: {response.status_code}")
                
        except Exception as e:
            return LLMResponse("", model, 0, False, str(e))
    
    def query_local_model(self, prompt: str, model: str = "llama2") -> LLMResponse:
        """Query local Ollama model"""
        try:
            response = requests.post(
                f"{self.local_model_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('response', '')
                return LLMResponse(content, model, 0, True)
            else:
                return LLMResponse("", model, 0, False, f"Local model error: {response.status_code}")
                
        except Exception as e:
            return LLMResponse("", model, 0, False, str(e))
    
    def generate_response(self, prompt: str, context: str = "", use_local: bool = False) -> LLMResponse:
        """Generate response with fallback logic"""
        system_prompt = """You are StarkAI, an AI assistant with Tony Stark's personality. 
        Be confident, slightly sarcastic, brilliant, and helpful. 
        Provide technical solutions while maintaining the Tony Stark persona."""
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        if use_local:
            response = self.query_local_model(full_prompt)
            if response.success:
                return response
        
        response = self.query_openai(full_prompt, system_prompt)
        if response.success:
            return response
        
        return LLMResponse(
            "My AI systems are temporarily offline. Even genius tech needs maintenance sometimes.",
            "fallback", 0, True
        )
    
    def analyze_code(self, code: str, language: str = "python") -> LLMResponse:
        """Analyze code for issues and improvements"""
        prompt = f"""Analyze this {language} code for bugs, improvements, and best practices:

```{language}
{code}
```

Provide:
1. Issues found
2. Suggested fixes
3. Code quality rating (1-10)
4. Improvement recommendations

Be thorough but concise."""
        
        return self.generate_response(prompt)
    
    def suggest_fix(self, code: str, error_message: str, language: str = "python") -> LLMResponse:
        """Suggest fixes for specific code errors"""
        prompt = f"""Fix this {language} code error:

Error: {error_message}

Code:
```{language}
{code}
```

Provide the corrected code and explanation."""
        
        return self.generate_response(prompt)
