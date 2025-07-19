"""
NOVA Interfaces - Abstract base classes for all components
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .models import SystemProfile, StorageConfig, UserProfile, Task, AIResponse, Model


class ISystemAnalyzer(ABC):
    """Interface for system analysis components"""
    
    @abstractmethod
    async def analyze_mac(self) -> SystemProfile:
        """Analyze Mac system and return profile"""
        pass


class IStorageManager(ABC):
    """Interface for storage management"""
    
    @abstractmethod
    async def setup_storage(self, config: StorageConfig) -> bool:
        """Set up storage based on configuration"""
        pass
        
    @abstractmethod
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get current storage information"""
        pass


class IModelManager(ABC):
    """Interface for AI model management"""
    
    @abstractmethod
    async def download_model(self, model_name: str) -> bool:
        """Download a model"""
        pass
        
    @abstractmethod
    async def get_available_models(self) -> List[Model]:
        """Get list of available models"""
        pass


class IMemorySystem(ABC):
    """Interface for memory system management"""
    
    @abstractmethod
    async def save_profile(self, profile: UserProfile) -> bool:
        """Save user profile"""
        pass
        
    @abstractmethod
    async def load_profile(self) -> Optional[UserProfile]:
        """Load user profile"""
        pass
        
    @abstractmethod
    async def add_conversation(self, user_profile: UserProfile, user_input: str, 
                             nova_response: str, model_used: str, actions: List[str],
                             context: Dict[str, Any], tokens: int, cost: float) -> bool:
        """Add conversation to memory"""
        pass


class IAIEngine(ABC):
    """Interface for AI reasoning engine"""
    
    @abstractmethod
    async def initialize(self, available_models: List[Model]) -> None:
        """Initialize AI engine with available models"""
        pass
        
    @abstractmethod
    async def process_task(self, task: Task) -> AIResponse:
        """Process a task and return AI response"""
        pass
        
    @abstractmethod
    async def switch_model(self, model_name: str) -> bool:
        """Switch to a different model"""
        pass


class IAutomationLayer(ABC):
    """Interface for Mac automation"""
    
    @abstractmethod
    async def execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute an automation action"""
        pass
        
    @abstractmethod
    async def get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        pass