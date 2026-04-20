"""
Ollama LLM implementation.
"""
from typing import AsyncIterator

import ollama

from app.llm.base import BaseLLM
from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import logger


class OllamaLLM(BaseLLM):
    """Ollama LLM implementation."""
    
    def __init__(self, model_name: str | None = None):
        """
        Initialize Ollama LLM.
        
        Args:
            model_name: Model name to use (defaults to config)
        """
        self._model_name = model_name or settings.ollama_llm_model
        logger.info(f"Initialized Ollama LLM: model={self._model_name}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ) -> str:
        """Generate text completion using Ollama."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = ollama.chat(
                model=self._model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            raise LLMError(
                f"Ollama generation failed: {str(e)}",
                details={"model": self._model_name}
            )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """Generate text completion with streaming using Ollama."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            stream = ollama.chat(
                model=self._model_name,
                messages=messages,
                stream=True,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )
            
            for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
            
        except Exception as e:
            raise LLMError(
                f"Ollama streaming failed: {str(e)}",
                details={"model": self._model_name}
            )
    
    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model_name
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "ollama"
