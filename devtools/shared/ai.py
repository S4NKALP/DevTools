"""
Shared AI service for devtools.
"""
import requests
import os
from typing import List, Dict, Optional, Any
from .config import BaseConfig

class AIService:
    """Base AI service that can be extended by specific tools."""
    
    def __init__(self, config: BaseConfig):
        """Initialize AI service with configuration."""
        self.config = config
        self._setup_ai()

    def _setup_ai(self) -> None:
        """Set up the AI model with configuration."""
        self.api_key = self.config.get_env_or_config("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please set it in config or environment.")
        
        self.model = self.config.get("model", "mistralai/mixtral-8x7b-instruct")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/S4NKALP/DevTools",
            "X-Title": "DevTools",
            "Content-Type": "application/json"
        }

    def _create_prompt(self, system_prompt: str, user_prompt: str) -> List[Dict[str, str]]:
        """Create a prompt for the AI model."""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def generate_completion(self, 
                          system_prompt: str,
                          user_prompt: str,
                          temperature: Optional[float] = None,
                          max_tokens: Optional[int] = None,
                          top_p: float = 0.95) -> str:
        """Generate a completion from the AI model."""
        messages = self._create_prompt(system_prompt, user_prompt)
        
        try:
            # Convert config values to proper types
            temp = temperature if temperature is not None else float(self.config.get("temperature", 0.7))
            tokens = max_tokens if max_tokens is not None else int(self.config.get("max_tokens", 150))
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                "top_p": float(top_p),
                "stream": False
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"]
                except:
                    pass
                raise Exception(f"OpenRouter API error: {error_msg}")
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            
            return ""
            
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")

    def generate_batch_completions(self,
                                 system_prompt: str,
                                 prompts: List[str],
                                 temperature: Optional[float] = None,
                                 max_tokens: Optional[int] = None) -> List[str]:
        """Generate completions for multiple prompts."""
        completions = []
        for prompt in prompts:
            completion = self.generate_completion(
                system_prompt,
                prompt,
                temperature,
                max_tokens
            )
            completions.append(completion)
        return completions 