"""
Ollama Client for NOVA
Simplified client for Ollama API interactions
"""

import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional


class OllamaClient:
    """
    Async client for Ollama API
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.logger = logging.getLogger('NOVA.OllamaClient')
        
    async def generate(self, model: str, prompt: str, temperature: float = 0.7) -> str:
        """Generate text using Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '')
                    else:
                        self.logger.error(f"Ollama generate failed: {response.status}")
                        return f"I apologize, but I couldn't generate a response. (Model: {model} may not be available)"
        except Exception as e:
            self.logger.error(f"Ollama generate error: {e}")
            return "I apologize, but I'm having trouble connecting to the AI model service."
            
    async def list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        result = await response.json()
                        models = result.get('models', [])
                        return [model['name'] for model in models]
                    else:
                        self.logger.error(f"Failed to list models: {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
            
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name, "stream": False}
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        self.logger.error(f"Failed to pull model {model_name}: {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"Error pulling model {model_name}: {e}")
            return False
            
    async def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/version") as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Ollama not available: {e}")
            return False


class OllamaManager:
    """
    Manager for Ollama operations
    """
    
    def __init__(self):
        self.client = OllamaClient()
        
    async def check_ollama(self) -> bool:
        """Check if Ollama is available"""
        return await self.client.check_ollama()
        
    async def list_models(self) -> List[str]:
        """List available models"""
        return await self.client.list_models()
        
    async def pull_model(self, model_name: str) -> bool:
        """Download a model"""
        return await self.client.pull_model(model_name)