#!/usr/bin/env python3
"""
NOVA Core Engine - Central orchestrator for all components
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid

from .system_analyzer import SmartSystemAnalyzer
from .storage_manager import StorageManager
from .model_manager import AdaptiveModelManager
from ..memory.persistent_memory import PersistentMemory
from ..setup.interactive_setup import InteractiveSetup
from ..ai.reasoning_engine import ReasoningEngine as AIReasoningEngine
from ..automation.mac_automation import MacAutomationLayer
from ..cli.terminal_interface import NOVATerminalInterface
from ..models import (
    SystemProfile,
    StorageConfig,
    UserProfile,
    Task,
    TaskComplexity,
    Model,
    ModelType,
    Command,
    CommandType
)

# Configure logging
log_dir = Path.home() / '.nova'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'nova.log'

# Remove the StreamHandler to avoid terminal spam
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a')
    ]
)


class NOVACore:
    """
    Central orchestrator that coordinates all NOVA components
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.Core')
        self.logger.info("NOVA Core initializing...")
        
        # Component initialization
        self.system_analyzer = SmartSystemAnalyzer()
        self.memory = PersistentMemory()
        self.storage_manager = StorageManager(Path.home() / '.nova')
        
        # Initialize model manager with correct path based on storage config
        storage_config = self.storage_manager.load_config()
        if storage_config and storage_config.use_external:
            models_path = storage_config.models_path
        else:
            models_path = Path.home() / '.nova' / 'models'
            
        self.model_manager = AdaptiveModelManager(models_path)
        self.ai_engine = AIReasoningEngine()
        self.automation = MacAutomationLayer()
        self.terminal = NOVATerminalInterface(nova_core=self)
        
        # State
        self.system_profile: Optional[SystemProfile] = None
        self.storage_config: Optional[StorageConfig] = None
        self.user_profile: Optional[UserProfile] = None
        self.is_first_run: bool = False
        self.background_tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self) -> bool:
        """Initialize NOVA system"""
        try:
            # Check if this is first run
            self.user_profile = await self.memory.load_profile()
            
            if self.user_profile is None:
                self.is_first_run = True
                return True  # Will run setup
                
            # Load existing configuration
            self.logger.info("Loading existing configuration...")
            
            # Re-analyze system (might have changed)
            self.system_profile = await self.system_analyzer.analyze_mac()
            
            # Initialize AI engine with available models
            available_models = self._get_available_models()
            await self.ai_engine.initialize(available_models)
            
            self.logger.info("NOVA initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
            
    async def run_first_time_setup(self) -> bool:
        """Run first-time setup"""
        try:
            setup = InteractiveSetup()
            
            # Run interactive setup
            self.system_profile, self.storage_config, self.user_profile = \
                await setup.run_first_time_setup()
                
            # Initialize AI engine with discovered capabilities
            available_models = self._get_available_models()
            await self.ai_engine.initialize(available_models)
            
            self.is_first_run = False
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False
            
    def _get_available_models(self) -> List[Model]:
        """Get available models - dynamically from Ollama and model manager"""
        models = []
        
        # Get ALL locally installed Ollama models
        try:
            discovered_models = self.model_manager.discover_models()
            models.extend(discovered_models)
            self.logger.info(f"Discovered {len(discovered_models)} Ollama models")
        except Exception as e:
            self.logger.warning(f"Could not discover Ollama models: {e}")
            
        # Add cloud models as fallback
        models.append(
            Model(
                name="groq-mixtral",
                type=ModelType.FREE_API,
                size_gb=None,
                context_window=32768,
                capabilities=["general", "code", "fast"],
                cost_per_1k_tokens=0.0,
                speed_score=10,
                quality_score=8
            )
        )
        
        # Premium (if API keys available)
        if os.environ.get('OPENAI_API_KEY'):
            models.append(
                Model(
                    name="gpt-4-turbo",
                    type=ModelType.PREMIUM_API,
                    size_gb=None,
                    context_window=128000,
                    capabilities=["general", "code", "reasoning", "vision"],
                    cost_per_1k_tokens=0.01,
                    speed_score=7,
                    quality_score=10
                )
            )
            
        return models
        
    async def process_user_request(self, request: str) -> Dict[str, Any]:
        """Process a user request and return response"""
        try:
            # Create task with context
            task = Task(
                content=request,
                complexity=self._analyze_complexity(request),
                context=self._build_context(),
                requires_code_gen=self._check_code_generation(request),
                requires_web_access=self._check_web_access(request)
            )
            
            # Process with AI engine
            ai_response = await self.ai_engine.process_task(task)
            
            # Execute actions if any
            actions_taken = []
            if ai_response.actions:
                for action in ai_response.actions:
                    success = await self._execute_action(action)
                    if success:
                        actions_taken.append(f"{action.type}: {action.target}")
                        
            # Save conversation
            await self.memory.add_conversation(
                self.user_profile,
                request,
                ai_response.content,
                ai_response.model_used,
                actions_taken,
                task.context,
                ai_response.tokens_used,
                ai_response.cost
            )
            
            return {
                'response': ai_response.content,
                'actions': actions_taken,
                'model': ai_response.model_used,
                'cost': ai_response.cost
            }
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return {
                'response': f"I encountered an error: {str(e)}",
                'actions': [],
                'model': 'none',
                'cost': 0.0
            }
            
    def _build_context(self) -> Dict[str, Any]:
        """Build context for AI processing"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'system_info': f"{self.system_profile.chip_generation} Mac" if self.system_profile else "Unknown",
            'current_directory': os.getcwd(),
            'user_preferences': {
                'performance_mode': self.user_profile.preferences.performance_mode,
                'preferred_stack': self.user_profile.preferences.preferred_stack
            } if self.user_profile else {}
        }
        
        # Add recent files if in a project directory
        try:
            recent_files = list(Path('.').glob('*'))[:10]
            context['recent_files'] = [f.name for f in recent_files if f.is_file()]
        except:
            pass
            
        return context
        
    def _analyze_complexity(self, request: str) -> TaskComplexity:
        """Analyze task complexity"""
        complex_keywords = ['build', 'create app', 'implement system', 'complex', 'multiple', 'architecture']
        medium_keywords = ['code', 'function', 'script', 'debug', 'fix', 'help', 'explain']
        
        if any(keyword in request.lower() for keyword in complex_keywords):
            return TaskComplexity.COMPLEX
        elif any(keyword in request.lower() for keyword in medium_keywords):
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.SIMPLE
        
    def _check_code_generation(self, request: str) -> bool:
        """Check if request requires code generation"""
        code_keywords = ['code', 'build', 'create', 'implement', 'function', 'class', 'app', 'script']
        return any(keyword in request.lower() for keyword in code_keywords)
        
    def _check_web_access(self, request: str) -> bool:
        """Check if request requires web access"""
        web_keywords = ['search', 'google', 'web', 'online', 'internet', 'download']
        return any(keyword in request.lower() for keyword in web_keywords)
        
    async def _execute_action(self, action) -> bool:
        """Execute an action using automation layer"""
        try:
            action_dict = {
                'type': action.type,
                'target': action.target,
                **action.params
            }
            
            return await self.automation.execute_action(action_dict)
            
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            return False
            
    async def start_background_task(self, task_description: str) -> str:
        """Start a background task"""
        task_id = str(uuid.uuid4())[:8]
        
        async def run_task():
            try:
                await self.process_user_request(task_description)
            except Exception as e:
                self.logger.error(f"Background task {task_id} failed: {e}")
                
        task = asyncio.create_task(run_task())
        self.background_tasks[task_id] = task
        
        return task_id
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        system_info = await self.automation.get_system_info()
        ai_info = self.ai_engine.get_model_info()
        memory_stats = await self.memory.get_memory_stats(self.user_profile)
        
        return {
            'system': {
                'tier': self.system_profile.performance_tier if self.system_profile else 'Unknown',
                'cpu': system_info.get('cpu_percent', 0),
                'memory_used': round(system_info.get('memory', {}).get('percent', 0) * 
                                   self.system_profile.ram_gb / 100, 1) if self.system_profile else 0,
                'memory_total': self.system_profile.ram_gb if self.system_profile else 0,
                'storage_free': round(system_info.get('disk', {}).get('free', 0) / (1024**3), 1)
            },
            'ai': ai_info,
            'tasks': {
                'active': len([t for t in self.background_tasks.values() if not t.done()]),
                'queued': 0
            },
            'memory': {
                'conversations': memory_stats['conversation_count'],
                'storage_mb': memory_stats['total_size_mb']
            }
        }
        
    async def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory summary for display"""
        if not self.user_profile:
            return {}
            
        recent_convs = [
            {
                'timestamp': conv.timestamp.strftime('%Y-%m-%d %H:%M'),
                'user_input': conv.user_input,
                'nova_response': conv.nova_response,
                'model': conv.model_used,
                'cost': conv.cost
            }
            for conv in self.user_profile.conversation_history[-10:]
        ]
        
        return {
            'created_at': self.user_profile.created_at.strftime('%Y-%m-%d'),
            'total_interactions': self.user_profile.total_interactions,
            'preferred_stack': self.user_profile.preferences.preferred_stack,
            'working_hours': self.user_profile.preferences.working_hours,
            'recent_projects': self.user_profile.recent_projects[-5:],
            'learned_patterns': dict(list(self.user_profile.learned_patterns.items())[:10]),
            'recent_conversations': recent_convs
        }
        
    async def save_session(self):
        """Save current session"""
        if self.user_profile:
            await self.memory.save_profile(self.user_profile)
            
    def get_current_model_name(self) -> str:
        """Get the current active model name"""
        if self.ai_engine and hasattr(self.ai_engine, 'active_model') and self.ai_engine.active_model:
            return self.ai_engine.active_model.name
        return "No model active"
            
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("NOVA shutting down...")
        
        # Cancel background tasks
        for task_id, task in self.background_tasks.items():
            if not task.done():
                task.cancel()
                
        # Save session
        await self.save_session()
        
        self.logger.info("NOVA shutdown complete")
        

async def main():
    """Main entry point"""
    # Create NOVA core
    nova = NOVACore()
    
    # Initialize
    if not await nova.initialize():
        print("Failed to initialize NOVA")
        return 1
        
    # Check if first run
    if nova.is_first_run:
        if not await nova.run_first_time_setup():
            print("Setup failed")
            return 1
            
    # Run the terminal interface
    await nova.terminal.run_interactive_mode()
    
    # Shutdown
    await nova.shutdown()
    
    return 0
    

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nNOVA: Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"NOVA: Fatal error: {e}")
        sys.exit(1)