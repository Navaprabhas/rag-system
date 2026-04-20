"""
OpenAI LLM implementation.
"""
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.llm.base import BaseLLM
from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import logger


class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation."""
    
    def __init__(self, model_name: str | None = None):
        """
        Initialize OpenAI LLM.
        
        Args:
            model_name: Model name to use
        """
        if not settings.openai_api_key:
            raise LLMError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model_name = model_name or "gpt-4o-mini"
        logger.info(f"Initialized OpenAI LLM: model={self._model_name}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ) -> str:
        """Generate text completion using OpenAI."""
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
            
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise LLMError(
                f"OpenAI generation failed: {str(e)}",
                details={"model": self._model_name}
            )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """Generate text completion with streaming using OpenAI."""
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
            
            stream = await self.client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
        except Exception as e:
            raise LLMError(
                f"OpenAI streaming failed: {str(e)}",
                details={"model": self._model_name}
            )
    
    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model_name
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "openai"
