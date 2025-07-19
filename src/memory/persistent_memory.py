import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import asyncio
import aiofiles
from cryptography.fernet import Fernet
import uuid

from ..models import UserProfile, Conversation, Preferences
from ..interfaces import IMemorySystem


class PersistentMemory(IMemorySystem):
    """
    Text-based memory that persists between sessions
    Uses markdown for human readability and JSON for structured data
    """
    
    def __init__(self, memory_path: Optional[Path] = None):
        self.logger = logging.getLogger('NOVA.Memory')
        
        # Default to ~/.nova/memory
        if memory_path is None:
            memory_path = Path.home() / '.nova' / 'memory'
            
        self.memory_path = memory_path
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.profile_file = self.memory_path / 'user_profile.json'
        self.memory_file = self.memory_path / 'memory.md'
        self.conversations_dir = self.memory_path / 'conversations'
        self.preferences_file = self.memory_path / 'preferences.json'
        
        # Create conversations directory
        self.conversations_dir.mkdir(exist_ok=True)
        
        # Initialize encryption for sensitive data
        self._init_encryption()
        
    def _init_encryption(self):
        """Initialize encryption for sensitive data"""
        key_file = self.memory_path / '.key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Make key file hidden and read-only
            os.chmod(key_file, 0o400)
            
        self.cipher = Fernet(key)
        
    async def load_profile(self) -> Optional[UserProfile]:
        """Load user profile from disk"""
        try:
            if not self.profile_file.exists():
                self.logger.info("No existing profile found")
                return None
                
            async with aiofiles.open(self.profile_file, 'r') as f:
                data = json.loads(await f.read())
                
            # Load preferences
            preferences = await self._load_preferences()
            
            # Load conversations
            conversations = await self._load_conversations(data.get('conversation_ids', []))
            
            # Create profile
            profile = UserProfile(
                created_at=datetime.fromisoformat(data['created_at']),
                last_active=datetime.fromisoformat(data['last_active']),
                preferences=preferences,
                recent_projects=data.get('recent_projects', []),
                conversation_history=conversations,
                learned_patterns=data.get('learned_patterns', {}),
                total_interactions=data.get('total_interactions', 0),
                total_cost=data.get('total_cost', 0.0)
            )
            
            self.logger.info(f"Loaded profile with {len(conversations)} conversations")
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to load profile: {e}")
            return None
            
    async def save_profile(self, profile: UserProfile) -> None:
        """Save user profile to disk"""
        try:
            # Save conversations first
            conversation_ids = await self._save_conversations(profile.conversation_history)
            
            # Save preferences
            await self._save_preferences(profile.preferences)
            
            # Save profile data
            data = {
                'created_at': profile.created_at.isoformat(),
                'last_active': profile.last_active.isoformat(),
                'recent_projects': profile.recent_projects,
                'conversation_ids': conversation_ids,
                'learned_patterns': profile.learned_patterns,
                'total_interactions': profile.total_interactions,
                'total_cost': profile.total_cost
            }
            
            async with aiofiles.open(self.profile_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
            # Update human-readable memory file
            await self._update_memory_markdown(profile)
            
            self.logger.info("Profile saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save profile: {e}")
            raise
            
    async def _load_preferences(self) -> Preferences:
        """Load user preferences"""
        try:
            if not self.preferences_file.exists():
                return Preferences()  # Return defaults
                
            async with aiofiles.open(self.preferences_file, 'r') as f:
                data = json.loads(await f.read())
                
            return Preferences(**data)
            
        except Exception as e:
            self.logger.error(f"Failed to load preferences: {e}")
            return Preferences()
            
    async def _save_preferences(self, preferences: Preferences) -> None:
        """Save user preferences"""
        data = {
            'performance_mode': preferences.performance_mode,
            'preferred_stack': preferences.preferred_stack,
            'coding_style': preferences.coding_style,
            'working_hours': preferences.working_hours,
            'auto_commit': preferences.auto_commit,
            'verbose_mode': preferences.verbose_mode,
            'prefer_local_models': preferences.prefer_local_models,
            'max_monthly_cost': preferences.max_monthly_cost,
            'theme': preferences.theme
        }
        
        async with aiofiles.open(self.preferences_file, 'w') as f:
            await f.write(json.dumps(data, indent=2))
            
    async def _load_conversations(self, conversation_ids: List[str]) -> List[Conversation]:
        """Load conversations from disk"""
        conversations = []
        
        for conv_id in conversation_ids[-100:]:  # Load last 100 conversations
            conv_file = self.conversations_dir / f"{conv_id}.json"
            
            if not conv_file.exists():
                continue
                
            try:
                async with aiofiles.open(conv_file, 'r') as f:
                    data = json.loads(await f.read())
                    
                # Decrypt sensitive fields if needed
                if 'encrypted_context' in data:
                    context_bytes = self.cipher.decrypt(data['encrypted_context'].encode())
                    data['context'] = json.loads(context_bytes.decode())
                    
                conversation = Conversation(
                    id=data['id'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    user_input=data['user_input'],
                    nova_response=data['nova_response'],
                    actions_taken=data['actions_taken'],
                    model_used=data['model_used'],
                    context=data.get('context', {}),
                    tokens_used=data.get('tokens_used', 0),
                    cost=data.get('cost', 0.0)
                )
                
                conversations.append(conversation)
                
            except Exception as e:
                self.logger.error(f"Failed to load conversation {conv_id}: {e}")
                
        return conversations
        
    async def _save_conversations(self, conversations: List[Conversation]) -> List[str]:
        """Save conversations and return their IDs"""
        conversation_ids = []
        
        for conversation in conversations:
            try:
                # Encrypt sensitive context
                context_json = json.dumps(conversation.context)
                encrypted_context = self.cipher.encrypt(context_json.encode()).decode()
                
                data = {
                    'id': conversation.id,
                    'timestamp': conversation.timestamp.isoformat(),
                    'user_input': conversation.user_input,
                    'nova_response': conversation.nova_response,
                    'actions_taken': conversation.actions_taken,
                    'model_used': conversation.model_used,
                    'encrypted_context': encrypted_context,
                    'tokens_used': conversation.tokens_used,
                    'cost': conversation.cost
                }
                
                conv_file = self.conversations_dir / f"{conversation.id}.json"
                async with aiofiles.open(conv_file, 'w') as f:
                    await f.write(json.dumps(data, indent=2))
                    
                conversation_ids.append(conversation.id)
                
            except Exception as e:
                self.logger.error(f"Failed to save conversation {conversation.id}: {e}")
                
        return conversation_ids
        
    async def _update_memory_markdown(self, profile: UserProfile) -> None:
        """Update human-readable memory file"""
        try:
            content = f"""# NOVA Memory

## User Profile

- **Created**: {profile.created_at.strftime('%Y-%m-%d')}
- **Last Active**: {profile.last_active.strftime('%Y-%m-%d %H:%M')}
- **Total Interactions**: {profile.total_interactions}
- **Total Cost**: ${profile.total_cost:.2f}

## Preferences

- **Performance Mode**: {profile.preferences.performance_mode}
- **Preferred Stack**: {', '.join(profile.preferences.preferred_stack)}
- **Working Hours**: {profile.preferences.working_hours or 'Not set'}
- **Monthly Budget**: ${profile.preferences.max_monthly_cost}
- **Prefer Local Models**: {profile.preferences.prefer_local_models}

## Recent Projects

"""
            
            for project in profile.recent_projects[:10]:
                if isinstance(project, dict):
                    content += f"- **{project.get('name', 'Unknown')}** - {project.get('description', '')} ({project.get('date', '')})\n"
                else:
                    # Handle simple string format
                    content += f"- {project}\n"
                
            content += "\n## Learned Patterns\n\n"
            
            for pattern, details in profile.learned_patterns.items():
                content += f"- **{pattern}**: {details}\n"
                
            content += "\n## Recent Conversations\n\n"
            
            for conv in profile.conversation_history[-10:]:
                content += f"""### {conv.timestamp.strftime('%Y-%m-%d %H:%M')}

**User**: {conv.user_input[:100]}...

**NOVA**: {conv.nova_response[:100]}...

**Model**: {conv.model_used} | **Cost**: ${conv.cost:.4f}

---

"""
                
            async with aiofiles.open(self.memory_file, 'w') as f:
                await f.write(content)
                
        except Exception as e:
            self.logger.error(f"Failed to update memory markdown: {e}")
            
    async def add_conversation(self, profile: UserProfile, user_input: str, 
                             nova_response: str, model_used: str,
                             actions_taken: List[Dict], context: Dict,
                             tokens_used: int = 0, cost: float = 0.0) -> None:
        """Add a new conversation to the profile"""
        conversation = Conversation(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_input=user_input,
            nova_response=nova_response,
            actions_taken=actions_taken,
            model_used=model_used,
            context=context,
            tokens_used=tokens_used,
            cost=cost
        )
        
        profile.add_conversation(conversation)
        
        # Save immediately for persistence
        await self.save_profile(profile)
        
    async def update_learned_patterns(self, profile: UserProfile, 
                                    pattern: str, details: Any) -> None:
        """Update learned patterns in profile"""
        profile.learned_patterns[pattern] = details
        profile.last_active = datetime.now()
        
        # Save immediately
        await self.save_profile(profile)
        
    async def search_conversations(self, profile: UserProfile, query: str, 
                                 limit: int = 10) -> List[Conversation]:
        """Search through conversation history"""
        return profile.get_relevant_history(query, limit)
        
    async def get_memory_stats(self, profile: UserProfile) -> Dict[str, Any]:
        """Get memory usage statistics"""
        # Calculate sizes
        total_size = sum(
            f.stat().st_size 
            for f in self.memory_path.rglob('*') 
            if f.is_file()
        )
        
        conversation_count = len(list(self.conversations_dir.glob('*.json')))
        
        return {
            'total_size_mb': total_size / (1024 * 1024),
            'conversation_count': conversation_count,
            'total_interactions': profile.total_interactions,
            'total_cost': profile.total_cost,
            'days_active': (datetime.now() - profile.created_at).days,
            'avg_daily_cost': profile.total_cost / max(1, (datetime.now() - profile.created_at).days)
        }
        
    async def cleanup_old_conversations(self, profile: UserProfile, 
                                      keep_last: int = 1000) -> int:
        """Clean up old conversations to save space"""
        if len(profile.conversation_history) <= keep_last:
            return 0
            
        # Keep only the last N conversations
        to_remove = len(profile.conversation_history) - keep_last
        removed_conversations = profile.conversation_history[:to_remove]
        profile.conversation_history = profile.conversation_history[to_remove:]
        
        # Delete old conversation files
        for conv in removed_conversations:
            conv_file = self.conversations_dir / f"{conv.id}.json"
            if conv_file.exists():
                conv_file.unlink()
                
        # Save updated profile
        await self.save_profile(profile)
        
        self.logger.info(f"Cleaned up {to_remove} old conversations")
        return to_remove
        
    async def load_storage_config(self) -> Optional[Dict]:
        """Load storage configuration"""
        try:
            # Check in the config directory first
            config_dir = Path.home() / '.nova' / 'config'
            storage_config_file = config_dir / 'storage_config.json'
            
            # Fallback to memory directory
            if not storage_config_file.exists():
                storage_config_file = self.memory_path / 'storage_config.json'
                
            if not storage_config_file.exists():
                return None
                
            async with aiofiles.open(storage_config_file, 'r') as f:
                return json.loads(await f.read())
                
        except Exception as e:
            self.logger.error(f"Failed to load storage config: {e}")
            return None