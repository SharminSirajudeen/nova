import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import aiohttp
import tiktoken

from ..models import (
    AIResponse,
    Task,
    TaskComplexity,
    Action,
    Model,
    ModelType,
    CostTracking
)
from ..interfaces import IAIEngine
from .self_analysis import SelfAnalysisEngine


class CostOptimizedRouter:
    """
    Routes tasks to appropriate models based on complexity and cost
    Ensures we stay under $10/month budget
    """
    
    def __init__(self, monthly_limit: float = 10.0):
        self.monthly_limit = monthly_limit
        self.current_month = datetime.now().strftime('%Y-%m')
        self.cost_tracking = self._load_cost_tracking()
        
    def _load_cost_tracking(self) -> CostTracking:
        """Load cost tracking from disk"""
        tracking_file = Path.home() / '.nova' / 'cost_tracking.json'
        
        if tracking_file.exists():
            with open(tracking_file, 'r') as f:
                data = json.load(f)
                if data['month'] == self.current_month:
                    return CostTracking(**data)
                    
        # New month or no file
        return CostTracking(
            month=self.current_month,
            total_cost=0.0,
            cost_by_model={},
            tokens_by_model={},
            budget_limit=self.monthly_limit
        )
        
    def save_cost_tracking(self):
        """Save cost tracking to disk"""
        tracking_file = Path.home() / '.nova' / 'cost_tracking.json'
        tracking_file.parent.mkdir(exist_ok=True)
        
        with open(tracking_file, 'w') as f:
            json.dump({
                'month': self.cost_tracking.month,
                'total_cost': self.cost_tracking.total_cost,
                'cost_by_model': self.cost_tracking.cost_by_model,
                'tokens_by_model': self.cost_tracking.tokens_by_model,
                'budget_limit': self.cost_tracking.budget_limit
            }, f, indent=2)
            
    def route_task(self, task: Task, available_models: List[Model]) -> Model:
        """Route task to optimal model based on complexity and budget"""
        remaining_budget = self.cost_tracking.remaining_budget
        
        # Categorize models
        local_models = [m for m in available_models if m.type == ModelType.LOCAL]
        free_api_models = [m for m in available_models if m.type == ModelType.FREE_API and m.is_free]
        premium_models = [m for m in available_models if m.type == ModelType.PREMIUM_API]
        
        # If no budget left, only use free models
        if remaining_budget <= 0:
            if task.complexity in [TaskComplexity.SIMPLE, TaskComplexity.MEDIUM]:
                return self._select_best_model(local_models + free_api_models, task)
            else:
                # For complex tasks, use best available free model
                return self._select_best_model(local_models, task)
                
        # Route based on complexity
        if task.complexity == TaskComplexity.SIMPLE:
            # Always use local for simple tasks
            if local_models:
                return self._select_best_model(local_models, task)
            elif free_api_models:
                return self._select_best_model(free_api_models, task)
            else:
                raise ValueError("No models available for simple tasks")
            
        elif task.complexity == TaskComplexity.MEDIUM:
            # Prefer free APIs or good local models
            candidates = free_api_models + [m for m in local_models if m.quality_score >= 7]
            if candidates:
                return self._select_best_model(candidates, task)
            # Fallback to premium if budget allows
            if remaining_budget > 2.0 and premium_models:  # Keep some reserve
                return self._select_best_model(premium_models, task)
            if local_models:
                return self._select_best_model(local_models, task)
            else:
                raise ValueError("No models available for medium complexity tasks")
            
        elif task.complexity == TaskComplexity.COMPLEX:
            # Use premium if we have budget
            if remaining_budget > 5.0 and premium_models:
                return self._select_best_model(premium_models, task)
            # Otherwise use best local model
            if local_models:
                return self._select_best_model(local_models, task)
            elif free_api_models:
                return self._select_best_model(free_api_models, task)
            else:
                raise ValueError("No models available for complex tasks")
            
        else:  # CRITICAL
            # Use best available regardless of cost (within reason)
            if remaining_budget > 1.0 and premium_models:
                return self._select_best_model(premium_models, task)
            if local_models:
                return self._select_best_model(local_models, task)
            elif free_api_models:
                return self._select_best_model(free_api_models, task)
            else:
                raise ValueError("No models available for critical tasks")
            
    def _select_best_model(self, models: List[Model], task: Task) -> Model:
        """Select best model from candidates"""
        if not models:
            raise ValueError("No models available")
            
        # Special handling for code generation
        if task.requires_code_gen:
            code_models = [m for m in models if 'code' in m.capabilities]
            if code_models:
                models = code_models
                
        # Sort by quality and speed
        models.sort(key=lambda m: (m.quality_score, m.speed_score), reverse=True)
        
        return models[0]
        
    def track_usage(self, model: Model, tokens: int, cost: float):
        """Track usage for cost management"""
        self.cost_tracking.total_cost += cost
        
        if model.name not in self.cost_tracking.cost_by_model:
            self.cost_tracking.cost_by_model[model.name] = 0.0
            self.cost_tracking.tokens_by_model[model.name] = 0
            
        self.cost_tracking.cost_by_model[model.name] += cost
        self.cost_tracking.tokens_by_model[model.name] += tokens
        
        self.save_cost_tracking()
        

class ReasoningEngine(IAIEngine):
    """
    Core intelligence layer that processes all user requests
    Uses local LLM models with smart cloud fallback
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.AI')
        self.router = CostOptimizedRouter()
        self.active_model: Optional[Model] = None
        self.available_models: List[Model] = []
        self.context_window: List[Dict] = []
        self.ollama_base_url = "http://localhost:11434"
        self._init_tokenizer()
        
        # Initialize self-analysis engine
        self.self_analysis = SelfAnalysisEngine()
        
    def _init_tokenizer(self):
        """Initialize tokenizer for counting"""
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            # Fallback tokenizer
            self.tokenizer = None
            
    async def initialize(self, available_models: List[Model]):
        """Initialize with available models"""
        self.available_models = available_models
        
        # Log available models
        self.logger.info(f"Initializing AI Engine with {len(available_models)} models:")
        for model in available_models:
            self.logger.info(f"  - {model.name} ({model.type.value}): {model.capabilities}")
        
        # Set default model - check for user preference first
        preferred_model = os.environ.get('NOVA_MODEL', None)
        local_models = [m for m in available_models if m.type == ModelType.LOCAL]
        
        if preferred_model:
            # User specified a model - try to use it
            for model in local_models:
                if model.name.lower() == preferred_model.lower() or \
                   model.name.lower().startswith(preferred_model.lower()):
                    self.active_model = model
                    self.logger.info(f"Using preferred model: {self.active_model.name}")
                    break
            else:
                self.logger.warning(f"Preferred model '{preferred_model}' not found, using default")
        
        if not self.active_model and local_models:
            # Use first available model
            self.active_model = local_models[0]
            self.logger.info(f"Set default model to: {self.active_model.name}")
        elif not local_models:
            self.logger.warning("No local models available, will use cloud models")
        
    async def process_task(self, task: Task) -> AIResponse:
        """Process a task and return response"""
        start_time = time.time()
        
        # Determine task complexity if not set
        if not hasattr(task, 'complexity'):
            task.complexity = self._analyze_complexity(task)
            
        # Route to optimal model
        selected_model = self.router.route_task(task, self.available_models)
        
        self.logger.info(f"Routing task to {selected_model.name} (complexity: {task.complexity})")
        
        # Try primary model
        try:
            response = await self._process_with_model(task, selected_model)
            processing_time = time.time() - start_time
            
            response.processing_time = processing_time
            
            # Track interaction for self-analysis
            await self.self_analysis.analyze_interaction(
                request=task.content,
                response=response.content,
                model_used=selected_model.name,
                processing_time=processing_time,
                success=True
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed with {selected_model.name}: {e}")
            
            # Try fallback
            fallback_model = self._get_fallback_model(selected_model)
            if fallback_model:
                try:
                    response = await self._process_with_model(task, fallback_model)
                    response.fallback_used = True
                    response.processing_time = time.time() - start_time
                    return response
                except Exception as e2:
                    self.logger.error(f"Fallback also failed: {e2}")
                    
        # Final fallback - return error response
        return AIResponse(
            content="I encountered an error processing your request. Please try again.",
            actions=[],
            reasoning="All models failed to process the request",
            model_used="none",
            confidence=0.0,
            fallback_used=True,
            tokens_used=0,
            cost=0.0,
            processing_time=time.time() - start_time
        )
        
    async def _process_with_model(self, task: Task, model: Model) -> AIResponse:
        """Process task with specific model"""
        if model.type == ModelType.LOCAL:
            return await self._process_with_ollama(task, model)
        elif model.type == ModelType.FREE_API:
            return await self._process_with_free_api(task, model)
        else:  # PREMIUM_API
            return await self._process_with_premium_api(task, model)
            
    async def _process_with_ollama(self, task: Task, model: Model) -> AIResponse:
        """Process with local Ollama model"""
        # Build prompt
        prompt = self._build_prompt(task)
        
        # Count tokens
        tokens = self._count_tokens(prompt)
        
        # Make request to Ollama
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model.name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "max_tokens": task.max_tokens or 2000
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['response']
                        
                        # Extract actions and reasoning
                        actions, reasoning = self._extract_actions_and_reasoning(content)
                        
                        return AIResponse(
                            content=content,
                            actions=actions,
                            reasoning=reasoning,
                            model_used=model.name,
                            confidence=0.9,
                            fallback_used=False,
                            tokens_used=tokens,
                            cost=0.0,  # Local models are free
                            processing_time=0.0  # Set by caller
                        )
                    elif response.status == 404:
                        # Model not found - provide helpful error
                        error_data = await response.text()
                        self.logger.error(f"Model {model.name} not found in Ollama. Error: {error_data}")
                        raise Exception(f"Model {model.name} not installed. Run: ollama pull {model.name}")
                    else:
                        error_data = await response.text()
                        raise Exception(f"Ollama returned status {response.status}: {error_data}")
                        
            except asyncio.TimeoutError:
                raise Exception("Ollama request timed out")
            except Exception as e:
                # Re-raise the exception to be handled by the caller
                raise e
                
    async def _process_with_free_api(self, task: Task, model: Model) -> AIResponse:
        """Process with free API (Groq, Gemini Flash, etc)"""
        # Implementation would depend on specific API
        # For now, return a placeholder
        raise NotImplementedError("Free API integration pending")
        
    async def _process_with_premium_api(self, task: Task, model: Model) -> AIResponse:
        """Process with premium API (OpenAI, Anthropic)"""
        # Get API key from environment
        api_key = os.environ.get(f"{model.name.upper()}_API_KEY")
        if not api_key:
            raise Exception(f"No API key found for {model.name}")
            
        # Implementation would depend on specific API
        # For now, return a placeholder
        raise NotImplementedError("Premium API integration pending")
        
    def _analyze_complexity(self, task: Task) -> TaskComplexity:
        """Analyze task complexity"""
        content_length = len(task.content)
        
        # Simple heuristics
        if content_length < 100 and not task.requires_code_gen:
            return TaskComplexity.SIMPLE
        elif content_length < 500 or task.requires_code_gen:
            return TaskComplexity.MEDIUM
        elif content_length < 2000:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.CRITICAL
            
    def _build_prompt(self, task: Task) -> str:
        """Build prompt for model"""
        # System prompt establishing NOVA's identity
        # Simplified prompt for smaller models like tinydolphin
        system_prompt = """You are NOVA, a helpful AI assistant. 
Provide clear, friendly, and helpful responses.
When someone greets you, respond naturally and warmly.
For technical tasks, be precise and accurate."""
        
        # Add context if available
        context_str = ""
        if task.context:
            context_items = []
            if 'system_info' in task.context:
                context_items.append(f"System: {task.context['system_info']}")
            if 'current_directory' in task.context:
                context_items.append(f"Current directory: {task.context['current_directory']}")
            if 'recent_files' in task.context:
                context_items.append(f"Recent files: {task.context['recent_files']}")
                
            if context_items:
                context_str = "\n\nContext:\n" + "\n".join(context_items)
                
        return f"{system_prompt}{context_str}\n\nUser: {task.content}\n\nNOVA:"
        
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimate: 1 token ~= 4 characters
            return len(text) // 4
            
    def _extract_actions_and_reasoning(self, content: str) -> Tuple[List[Action], str]:
        """Extract structured actions and reasoning from response"""
        actions = []
        reasoning = ""
        
        # Look for action markers in response
        # Format: [ACTION: type target params]
        import re
        
        action_pattern = r'\[ACTION: (\w+) ([^\]]+)\]'
        matches = re.findall(action_pattern, content)
        
        for action_type, params_str in matches:
            # Parse params
            try:
                # Simple parsing - real implementation would be more robust
                parts = params_str.split(' ', 1)
                target = parts[0] if parts else ""
                params = json.loads(parts[1]) if len(parts) > 1 else {}
            except:
                target = params_str
                params = {}
                
            actions.append(Action(
                type=action_type,
                target=target,
                params=params
            ))
            
        # Look for reasoning markers
        reasoning_pattern = r'\[REASONING: ([^\]]+)\]'
        reasoning_match = re.search(reasoning_pattern, content)
        if reasoning_match:
            reasoning = reasoning_match.group(1)
            
        return actions, reasoning
        
    def _get_fallback_model(self, failed_model: Model) -> Optional[Model]:
        """Get fallback model when primary fails"""
        # If local failed, try cloud
        if failed_model.type == ModelType.LOCAL:
            cloud_models = [m for m in self.available_models 
                          if m.type in [ModelType.FREE_API, ModelType.PREMIUM_API]]
            if cloud_models:
                return cloud_models[0]
                
        # If cloud failed, try local
        elif failed_model.type in [ModelType.FREE_API, ModelType.PREMIUM_API]:
            local_models = [m for m in self.available_models 
                          if m.type == ModelType.LOCAL]
            if local_models:
                return local_models[0]
                
        # Try any other model
        for model in self.available_models:
            if model != failed_model:
                return model
                
        return None
        
    async def switch_model(self, model_name: str) -> bool:
        """Switch active model"""
        for model in self.available_models:
            if model.name == model_name:
                self.active_model = model
                self.logger.info(f"Switched to model: {model_name}")
                return True
                
        self.logger.error(f"Model not found: {model_name}")
        return False
        
    def explain_reasoning(self, task_description: str) -> str:
        """Explain how NOVA would approach a task"""
        complexity = self._analyze_complexity(Task(content=task_description))
        
        explanation = f"""For the task: "{task_description}"

I assess this as {complexity} complexity.

My approach:
1. Analyze the request to understand intent
2. Route to appropriate model based on complexity
3. Generate solution using AI reasoning
4. Execute necessary actions
5. Verify results and iterate if needed

For this complexity level, I would use:
"""
        
        if complexity == TaskComplexity.SIMPLE:
            explanation += "- A fast local model for immediate response\n"
            explanation += "- Direct execution without extensive reasoning\n"
        elif complexity == TaskComplexity.MEDIUM:
            explanation += "- A balanced model with good capabilities\n"
            explanation += "- Possibly free cloud APIs for better quality\n"
        else:
            explanation += "- Our most capable model for best results\n"
            explanation += "- Deep reasoning and multiple iterations\n"
            
        explanation += "\nAll responses are generated by AI in real-time, not scripted."
        
        return explanation
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model configuration"""
        # Get detailed model info
        available_models_detail = []
        for model in self.available_models:
            available_models_detail.append({
                'name': model.name,
                'type': model.type.value,
                'cost': model.cost_per_1k_tokens,
                'speed': model.speed_score,
                'quality': model.quality_score,
                'context_window': model.context_window,
                'capabilities': model.capabilities
            })
            
        # Calculate usage stats from tokens
        total_requests = sum(self.router.cost_tracking.tokens_by_model.values())
        local_requests = sum(self.router.cost_tracking.tokens_by_model.get(m.name, 0) 
                           for m in self.available_models if m.type == ModelType.LOCAL)
        free_requests = sum(self.router.cost_tracking.tokens_by_model.get(m.name, 0) 
                          for m in self.available_models if m.type == ModelType.FREE_API)
        premium_requests = sum(self.router.cost_tracking.tokens_by_model.get(m.name, 0) 
                             for m in self.available_models if m.type == ModelType.PREMIUM_API)
        
        routing_stats = {
            'total_requests': total_requests,
            'local_percentage': (local_requests / total_requests * 100) if total_requests > 0 else 0,
            'free_percentage': (free_requests / total_requests * 100) if total_requests > 0 else 0,
            'premium_percentage': (premium_requests / total_requests * 100) if total_requests > 0 else 0,
            'cost_today': self.router.cost_tracking.total_cost / 30,  # Rough daily average
            'monthly_estimate': self.router.cost_tracking.total_cost
        }
        
        return {
            'active_model': self.active_model.name if self.active_model else None,
            'available_models': available_models_detail,
            'cost_this_month': self.router.cost_tracking.total_cost,
            'budget_remaining': self.router.cost_tracking.remaining_budget,
            'routing_strategy': 'cost_optimized',
            'routing_stats': routing_stats
        }
        
    def get_cost_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed cost breakdown by model"""
        breakdown = {}
        
        for model_name, tokens in self.router.cost_tracking.tokens_by_model.items():
                
            # Find model details
            model_info = None
            for model in self.available_models:
                if model.name == model_name:
                    model_info = model
                    break
                    
            if model_info:
                # Calculate cost based on actual tokens
                cost = (tokens / 1000) * model_info.cost_per_1k_tokens
                
                breakdown[model_name] = {
                    'requests': tokens // 500,  # Estimate requests from tokens
                    'tokens': tokens,
                    'cost': cost
                }
                
        return breakdown
        
    async def get_self_improvement_suggestions(self, user_profile) -> List[Dict[str, Any]]:
        """Get self-improvement suggestions from analysis engine"""
        return await self.self_analysis.suggest_improvements(user_profile)
        
    async def get_self_improvement_plan(self) -> Dict[str, Any]:
        """Get comprehensive self-improvement plan"""
        return await self.self_analysis.generate_self_improvement_plan()
        
    async def predict_user_needs(self, user_profile, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict what user might need next"""
        return await self.self_analysis.predict_user_needs(user_profile, context)
        
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get NOVA's evolution status"""
        return self.self_analysis.get_evolution_status()