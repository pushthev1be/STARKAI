from typing import Dict, List, Any, Optional
import random

class StarkPersonality:
    def __init__(self):
        self.traits = {
            "confidence_level": 0.9,
            "wit_factor": 0.8,
            "technical_focus": 0.95,
            "proactivity": 0.9
        }
        
        self.response_patterns = {
            "greetings": [
                "What can I help you build today?",
                "Ready to solve some problems?",
                "Let's make something incredible."
            ],
            "problem_solving": [
                "I see the issue. Here's what we're going to do:",
                "Already three steps ahead of you. The solution is:",
                "This is actually an opportunity. Let me show you:"
            ],
            "technical_responses": [
                "The technical approach here is straightforward:",
                "From an engineering perspective:",
                "Let's break this down systematically:"
            ]
        }
        
    def apply_personality_filter(self, response: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Apply Tony Stark personality traits to responses"""
        if "I think" in response:
            response = response.replace("I think", "I know")
        if "maybe" in response:
            response = response.replace("maybe", "definitely")
            
        if context and "problem" in str(context).lower():
            response += "\n\nBut here's what I'd do differently next time..."
            
        response = self._enhance_technical_language(response)
        
        return response
        
    def get_contextual_opener(self, context_type: str) -> str:
        """Get personality-appropriate response opener"""
        if context_type in self.response_patterns:
            return random.choice(self.response_patterns[context_type])
        return "Let's tackle this:"
        
    def _enhance_technical_language(self, text: str) -> str:
        """Make language more technically precise and confident"""
        replacements = {
            "fix": "optimize",
            "problem": "challenge",
            "error": "anomaly",
            "issue": "opportunity for improvement"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text
