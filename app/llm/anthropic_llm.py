"""
Anthropic Claude LLM implementation.
"""
from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.llm.base import BaseLLM
from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import logger


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM implementation."""
    
    def __init__(self, model_name: str | None = None):
        """
        Initialize Anthropic LLM.
        
        Args:
            model_name: Model name to use
        """
        if not settings.anthropic_api_key:
            raise LLMError("Anthropic API key not configured")
        
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model_name = model_name or "claude-3-haiku-20240307"
        logger.info(f"Initialized Anthropic LLM: model={self._model_name}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ) -> str:
        """Generate text completion using Anthropic."""
        try:
            response = await self.client.messages.create(
                model=self._model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise LLMError(
                f"Anthropic generation failed: {str(e)}",
                details={"model": self._model_name}
            )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """Generate text completion with streaming using Anthropic."""
        try:
            async with self.client.messages.stream(
                model=self._model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
            
        except Exception as e:
            raise LLMError(
                f"Anthropic streaming failed: {str(e)}",
                details={"model": self._model_name}
            )
    
    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model_name
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "anthropic"
