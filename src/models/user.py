from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class Preferences:
    """User preferences"""
    performance_mode: str = "balanced"  # maximum, balanced, efficient
    preferred_stack: List[str] = field(default_factory=list)
    coding_style: Dict[str, str] = field(default_factory=dict)
    working_hours: Optional[str] = None
    auto_commit: bool = False
    verbose_mode: bool = False
    prefer_local_models: bool = True
    max_monthly_cost: float = 10.0
    theme: str = "auto"  # auto, light, dark
    

@dataclass
class Conversation:
    """Single conversation record"""
    id: str
    timestamp: datetime
    user_input: str
    nova_response: str
    actions_taken: List[Dict[str, Any]]
    model_used: str
    context: Dict[str, Any]
    tokens_used: int = 0
    cost: float = 0.0
    

@dataclass
class UserProfile:
    """Complete user profile with history and preferences"""
    created_at: datetime
    last_active: datetime
    preferences: Preferences
    recent_projects: List[Dict[str, Any]]
    conversation_history: List[Conversation]
    learned_patterns: Dict[str, Any]
    total_interactions: int = 0
    total_cost: float = 0.0
    
    @property
    def active_project(self) -> Optional[Dict[str, Any]]:
        """Get most recent project"""
        return self.recent_projects[0] if self.recent_projects else None
        
    def add_conversation(self, conversation: Conversation) -> None:
        """Add conversation to history"""
        self.conversation_history.append(conversation)
        self.total_interactions += 1
        self.total_cost += conversation.cost
        self.last_active = datetime.now()
        
    def get_relevant_history(self, query: str, limit: int = 5) -> List[Conversation]:
        """Get conversations relevant to query"""
        # Simple keyword matching for now
        # Could be enhanced with embeddings
        keywords = query.lower().split()
        relevant = []
        
        for conv in reversed(self.conversation_history):
            if any(kw in conv.user_input.lower() for kw in keywords):
                relevant.append(conv)
                if len(relevant) >= limit:
                    break
                    
        return relevant