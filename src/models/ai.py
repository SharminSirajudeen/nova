from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class TaskComplexity(str, Enum):
    """Task complexity levels for routing"""
    SIMPLE = "simple"  # Local small models
    MEDIUM = "medium"  # Local large models or free APIs
    COMPLEX = "complex"  # Premium APIs
    CRITICAL = "critical"  # Best available model
    

class ModelType(str, Enum):
    """Types of models"""
    LOCAL = "local"
    FREE_API = "free_api"
    PREMIUM_API = "premium_api"
    

@dataclass
class Model:
    """AI model information"""
    name: str
    type: ModelType
    size_gb: Optional[float]  # None for APIs
    context_window: int
    capabilities: List[str]
    cost_per_1k_tokens: float  # 0 for local
    speed_score: int  # 1-10
    quality_score: int  # 1-10
    
    @property
    def is_local(self) -> bool:
        return self.type == ModelType.LOCAL
        
    @property 
    def is_free(self) -> bool:
        return self.cost_per_1k_tokens == 0
        

@dataclass
class Task:
    """Task to be processed by AI"""
    content: str
    complexity: TaskComplexity
    context: Dict[str, Any] = field(default_factory=dict)
    requires_code_gen: bool = False
    requires_web_access: bool = False
    max_tokens: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    

@dataclass
class Action:
    """Action to be performed based on AI response"""
    type: str  # execute_code, run_command, etc
    target: str
    params: Dict[str, Any]
    

@dataclass
class AIResponse:
    """Response from AI processing"""
    content: str
    actions: List[Action]
    reasoning: str
    model_used: str
    confidence: float  # 0-1
    fallback_used: bool
    tokens_used: int
    cost: float
    processing_time: float  # seconds
    
    @property
    def success(self) -> bool:
        return self.confidence > 0.7
        

@dataclass
class CostTracking:
    """Track costs for the month"""
    month: str  # YYYY-MM
    total_cost: float
    cost_by_model: Dict[str, float]
    tokens_by_model: Dict[str, int]
    budget_limit: float = 10.0
    
    @property
    def remaining_budget(self) -> float:
        return max(0, self.budget_limit - self.total_cost)
        
    @property
    def budget_percent_used(self) -> float:
        return (self.total_cost / self.budget_limit) * 100