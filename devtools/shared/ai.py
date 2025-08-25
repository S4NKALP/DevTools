"""
Shared AI service for devtools.
"""

import requests
import os
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from .config import BaseConfig


class AIProvider(ABC):
    """Base class for AI providers."""

    @abstractmethod
    def setup(self, config: BaseConfig) -> None:
        """Set up the provider with configuration."""
        pass

    @abstractmethod
    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
    ) -> str:
        """Generate a completion from the AI model."""
        pass


class OpenRouterProvider(AIProvider):
    """OpenRouter AI provider implementation."""

    def setup(self, config: BaseConfig) -> None:
        self.config = config
        self.api_key = config.get_env_or_config("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Please set it in config or environment."
            )

        self.model = config.get("model", "mistralai/mixtral-8x7b-instruct")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/S4NKALP/DevTools",
            "X-Title": "DevTools",
            "Content-Type": "application/json",
        }

    def _create_prompt(
        self, system_prompt: str, user_prompt: str
    ) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
    ) -> str:
        messages = self._create_prompt(system_prompt, user_prompt)

        try:
            temp = (
                temperature
                if temperature is not None
                else float(self.config.get("temperature", 0.7))
            )
            tokens = (
                max_tokens
                if max_tokens is not None
                else int(self.config.get("max_tokens", 150))
            )

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                "top_p": float(top_p),
                "stream": False,
            }

            payload = {k: v for k, v in payload.items() if v is not None}

            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=30
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


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""

    def setup(self, config: BaseConfig) -> None:
        self.config = config
        self.api_key = config.get_env_or_config("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set it in config or environment."
            )

        self.model = config.get("model", "gpt-4-turbo-preview")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _create_prompt(
        self, system_prompt: str, user_prompt: str
    ) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
    ) -> str:
        messages = self._create_prompt(system_prompt, user_prompt)

        try:
            temp = (
                temperature
                if temperature is not None
                else float(self.config.get("temperature", 0.7))
            )
            tokens = (
                max_tokens
                if max_tokens is not None
                else int(self.config.get("max_tokens", 150))
            )

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                "top_p": float(top_p),
            }

            payload = {k: v for k, v in payload.items() if v is not None}

            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=30
            )

            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"]
                except:
                    pass
                raise Exception(f"OpenAI API error: {error_msg}")

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()

            return ""

        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""

    def setup(self, config: BaseConfig) -> None:
        self.config = config
        self.api_key = config.get_env_or_config("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Please set it in config or environment."
            )

        self.model = config.get("model", "gemini-pro")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self.headers = {"Content-Type": "application/json"}

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
    ) -> str:
        try:
            temp = (
                temperature
                if temperature is not None
                else float(self.config.get("temperature", 0.7))
            )
            tokens = (
                max_tokens
                if max_tokens is not None
                else int(self.config.get("max_tokens", 150))
            )

            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": temp,
                    "maxOutputTokens": tokens,
                    "topP": float(top_p),
                },
            }

            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=self.headers,
                json=payload,
                timeout=30,
            )

            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"]["message"]
                except:
                    pass
                raise Exception(f"Gemini API error: {error_msg}")

            result = response.json()

            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"].strip()

            return ""

        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider implementation."""

    def setup(self, config: BaseConfig) -> None:
        self.config = config
        self.api_key = config.get_env_or_config("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Please set it in config or environment."
            )

        self.model = config.get("model", "claude-3-opus-20240229")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _create_prompt(
        self, system_prompt: str, user_prompt: str
    ) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
    ) -> str:
        messages = self._create_prompt(system_prompt, user_prompt)

        try:
            temp = (
                temperature
                if temperature is not None
                else float(self.config.get("temperature", 0.7))
            )
            tokens = (
                max_tokens
                if max_tokens is not None
                else int(self.config.get("max_tokens", 150))
            )

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                "top_p": float(top_p),
            }

            payload = {k: v for k, v in payload.items() if v is not None}

            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=30
            )

            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"]["message"]
                except:
                    pass
                raise Exception(f"Claude API error: {error_msg}")

            result = response.json()

            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"].strip()

            return ""

        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")


class HuggingFaceProvider(AIProvider):
    """Hugging Face provider implementation."""

    def setup(self, config: BaseConfig) -> None:
        self.config = config
        self.api_key = config.get_env_or_config("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Hugging Face API key not found. Please set it in config or environment."
            )

        self.model = config.get("model", "mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _create_prompt(self, system_prompt: str, user_prompt: str) -> str:
        # Format prompt according to model's requirements
        return f"<s>[INST] {system_prompt}\n\n{user_prompt} [/INST]"

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
    ) -> str:
        try:
            temp = (
                temperature
                if temperature is not None
                else float(self.config.get("temperature", 0.7))
            )
            tokens = (
                max_tokens
                if max_tokens is not None
                else int(self.config.get("max_tokens", 150))
            )

            prompt = self._create_prompt(system_prompt, user_prompt)

            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": temp,
                    "max_new_tokens": tokens,
                    "top_p": float(top_p),
                    "return_full_text": False,
                },
            }

            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=30
            )

            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = error_json["error"]
                except:
                    pass
                raise Exception(f"Hugging Face API error: {error_msg}")

            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                return result[0]["generated_text"].strip()

            return ""

        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")


class AIService:
    """Base AI service that can be extended by specific tools."""

    def __init__(self, config: BaseConfig):
        """Initialize AI service with configuration."""
        self.config = config
        self.provider = self._get_provider()
        self.provider.setup(config)

    def _get_provider(self) -> AIProvider:
        """Get the appropriate AI provider based on configuration."""
        provider = self.config.get("provider", "openrouter").lower()

        providers = {
            "openrouter": OpenRouterProvider,
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "claude": ClaudeProvider,
            "huggingface": HuggingFaceProvider,
        }

        if provider not in providers:
            raise ValueError(
                f"Unsupported AI provider: {provider}. Supported providers: {', '.join(providers.keys())}"
            )

        return providers[provider]()

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
    ) -> str:
        """Generate a completion from the AI model."""
        return self.provider.generate_completion(
            system_prompt, user_prompt, temperature, max_tokens, top_p
        )

    def generate_batch_completions(
        self,
        system_prompt: str,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> List[str]:
        """Generate completions for multiple prompts."""
        completions = []
        for prompt in prompts:
            completion = self.generate_completion(
                system_prompt, prompt, temperature, max_tokens
            )
            completions.append(completion)
        return completions
