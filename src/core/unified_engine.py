"""
Unified Engine for NOVA
Combines ReasoningEngine with PersonalityEngine for multi-mode operation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ..ai.reasoning_engine import ReasoningEngine, AIResponse
from ..legendary.personalities.personality_engine import PersonalityEngine
from ..legendary.personalities.legendary_personalities import LegendaryPersonality
from ..models import Task, Model
from ..utils.ollama_client import OllamaClient


class OperationMode(Enum):
    """NOVA operation modes"""
    PERSONAL = "personal"
    COMPANY = "company"


@dataclass
class UnifiedResponse:
    """Response from unified engine"""
    content: str
    mode: OperationMode
    model_used: str
    personality_used: Optional[LegendaryPersonality]
    reasoning: str
    actions: List[Dict[str, Any]]
    tokens_used: int
    cost: float
    metadata: Dict[str, Any]


class UnifiedEngine:
    """
    Unified reasoning engine that supports both personal and company modes
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.UnifiedEngine')
        
        # Initialize both engines
        self.reasoning_engine = ReasoningEngine()
        self.personality_engine = PersonalityEngine()
        
        # Ollama client for company mode
        self.ollama = OllamaClient()
        
        # Current mode
        self.mode = OperationMode.PERSONAL
        
        # Available models (shared between modes)
        self.available_models: List[Model] = []
        
    async def initialize(self, available_models: List[Model]):
        """Initialize the unified engine"""
        self.available_models = available_models
        
        # Initialize reasoning engine (personal mode)
        await self.reasoning_engine.initialize(available_models)
        
        # Personality engine doesn't need async init
        self.logger.info(f"Unified engine initialized with {len(available_models)} models")
        
    def set_mode(self, mode: OperationMode):
        """Switch operation mode"""
        self.mode = mode
        self.logger.info(f"Switched to {mode.value} mode")
        
    async def process_task(self, task: Task) -> UnifiedResponse:
        """
        Process a task based on current mode
        """
        if self.mode == OperationMode.PERSONAL:
            return await self._process_personal_mode(task)
        else:
            return await self._process_company_mode(task)
            
    async def _process_personal_mode(self, task: Task) -> UnifiedResponse:
        """Process task in personal assistant mode"""
        # Use standard reasoning engine
        ai_response = await self.reasoning_engine.process_task(task)
        
        return UnifiedResponse(
            content=ai_response.content,
            mode=OperationMode.PERSONAL,
            model_used=ai_response.model_used,
            personality_used=None,
            reasoning=ai_response.reasoning_path,
            actions=ai_response.actions,
            tokens_used=ai_response.tokens_used,
            cost=ai_response.cost,
            metadata={
                'confidence': ai_response.confidence,
                'sub_queries': ai_response.sub_queries
            }
        )
        
    async def _process_company_mode(self, task: Task) -> UnifiedResponse:
        """Process task in company mode with personalities"""
        # Select personality
        personality, reasoning = self.personality_engine.select_personality(task)
        
        # Build personality-enhanced prompt
        enhanced_prompt = self.personality_engine.build_prompt(
            task=task,
            personality=personality,
            context=task.context
        )
        
        # Select model based on personality and task
        model = self._select_model_for_personality(personality, task)
        
        # Generate response
        try:
            response = await self.ollama.generate(
                model=model.name,
                prompt=enhanced_prompt,
                temperature=self.personality_engine.get_temperature(personality)
            )
            
            # Extract actions from response
            actions = self._extract_actions(response)
            
            # Estimate tokens (rough)
            tokens_used = len(enhanced_prompt.split()) + len(response.split())
            
            return UnifiedResponse(
                content=response,
                mode=OperationMode.COMPANY,
                model_used=model.name,
                personality_used=personality,
                reasoning=reasoning,
                actions=actions,
                tokens_used=tokens_used,
                cost=model.cost_per_1k_tokens * (tokens_used / 1000) if model.cost_per_1k_tokens else 0.0,
                metadata={
                    'personality_traits': personality.value,
                    'task_complexity': task.complexity.value,
                    'temperature': self.personality_engine.get_temperature(personality)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Company mode processing failed: {e}")
            # Fallback to personal mode
            return await self._process_personal_mode(task)
            
    def _select_model_for_personality(self, personality: LegendaryPersonality, task: Task) -> Model:
        """Select the best model for a personality and task"""
        # Personality preferences
        personality_preferences = {
            LegendaryPersonality.BUFFETT: lambda m: m.quality_score * 0.7 + m.speed_score * 0.3,
            LegendaryPersonality.LINUS: lambda m: m.quality_score * 0.9 + m.speed_score * 0.1,
            LegendaryPersonality.JOBS: lambda m: m.quality_score * 1.0,
            LegendaryPersonality.IVE: lambda m: m.quality_score * 0.8 + m.speed_score * 0.2,
            LegendaryPersonality.MUSK: lambda m: m.speed_score * 0.7 + m.quality_score * 0.3,
            LegendaryPersonality.CARMACK: lambda m: m.speed_score * 0.5 + m.quality_score * 0.5,
            LegendaryPersonality.HYBRID: lambda m: m.quality_score * 0.6 + m.speed_score * 0.4
        }
        
        # Get scoring function for personality
        score_func = personality_preferences.get(
            personality,
            lambda m: m.quality_score * 0.6 + m.speed_score * 0.4
        )
        
        # Filter and score models
        suitable_models = []
        for model in self.available_models:
            # Skip if model lacks required capabilities
            if task.requires_code_gen and 'code' not in model.capabilities:
                continue
                
            score = score_func(model)
            suitable_models.append((model, score))
            
        # Sort by score and return best
        suitable_models.sort(key=lambda x: x[1], reverse=True)
        
        if suitable_models:
            return suitable_models[0][0]
        else:
            # Fallback to first available model
            return self.available_models[0]
            
    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """Extract actionable items from response"""
        actions = []
        
        # Look for action patterns
        lines = response.split('\n')
        for line in lines:
            if any(marker in line for marker in ['TODO:', 'ACTION:', 'TASK:', '- [ ]']):
                actions.append({
                    'type': 'task',
                    'description': line.strip(),
                    'status': 'pending'
                })
                
        return actions
        
    def get_current_mode(self) -> str:
        """Get current operation mode"""
        return self.mode.value
        
    def get_personality_stats(self) -> Dict[str, Any]:
        """Get personality usage stats (company mode only)"""
        if self.mode == OperationMode.COMPANY:
            return self.personality_engine.get_stats()
        else:
            return {'mode': 'personal', 'message': 'Personality stats only available in company mode'}
            
    async def explain_approach(self, query: str) -> str:
        """Explain how the engine would approach a query"""
        task = Task(
            content=query,
            complexity=self.reasoning_engine._assess_complexity(query),
            context={},
            requires_code_gen=False,
            requires_web_access=False
        )
        
        if self.mode == OperationMode.PERSONAL:
            # Use reasoning engine's explanation
            return f"""
Operating in PERSONAL mode:

Task: "{query}"
Complexity: {task.complexity.value}

The reasoning engine would:
1. Assess task complexity and requirements
2. Select optimal model based on capabilities
3. Build context-aware prompt
4. Process through multi-step reasoning if needed
5. Extract and validate actions

This mode focuses on being a helpful personal assistant with practical solutions.
"""
        else:
            # Use personality engine's explanation
            personality, reasoning = self.personality_engine.select_personality(task)
            model = self._select_model_for_personality(personality, task)
            
            return f"""
Operating in COMPANY mode:

Task: "{query}"
Selected Personality: {personality.value} - {reasoning}
Model: {model.name}

{self.personality_engine.get_approach(personality, task)}

This mode brings the expertise and perspective of legendary tech leaders to the task.
"""