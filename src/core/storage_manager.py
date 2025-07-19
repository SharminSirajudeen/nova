import os
import json
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import asyncio

from ..models import StorageConfig, ExternalStorageConfig, InternalStorageConfig
from ..interfaces import IStorageManager


class StorageManager(IStorageManager):
    """
    Manages storage for NOVA including model storage, memory, and cleanup
    """
    
    def __init__(self, nova_home: Path):
        self.nova_home = nova_home
        self.logger = logging.getLogger('NOVA.Storage')
        
        # Create directory structure
        self.dirs = {
            'config': nova_home / 'config',
            'models': nova_home / 'models', 
            'memory': nova_home / 'memory',
            'logs': nova_home / 'logs',
            'temp': nova_home / 'temp',
            'scripts': nova_home / 'scripts'
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Storage configuration
        self.config: Optional[StorageConfig] = None
        self.load_config()
        
    def load_config(self) -> Optional[StorageConfig]:
        """Load storage configuration"""
        config_file = self.dirs['config'] / 'storage_config.json'
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    
                # Convert string paths back to Path objects
                if data.get('external_path'):
                    data['external_path'] = Path(data['external_path'])
                if data.get('internal_path'):
                    data['internal_path'] = Path(data['internal_path'])
                    
                if data['use_external']:
                    self.config = ExternalStorageConfig(**data)
                else:
                    self.config = InternalStorageConfig(**data)
                    
                return self.config
            except Exception as e:
                self.logger.error(f"Failed to load storage config: {e}")
                
        return None
        
    def save_config(self, config: StorageConfig):
        """Save storage configuration"""
        self.config = config
        config_file = self.dirs['config'] / 'storage_config.json'
        
        # Convert to dict, handling Path objects
        data = {
            'use_external': config.use_external,
            'external_path': str(config.external_path) if config.external_path else None,
            'internal_path': str(config.internal_path),
            'strategy': config.strategy,
            'prefer_cloud_apis': config.prefer_cloud_apis,
            'auto_cleanup': config.auto_cleanup,
            'min_free_space_gb': config.min_free_space_gb
        }
        
        # Add type-specific fields
        if isinstance(config, ExternalStorageConfig):
            data.update({
                'drive_name': config.drive_name,
                'drive_total_gb': config.drive_total_gb,
                'drive_available_gb': config.drive_available_gb,
                'drive_format': config.drive_format,
                'is_encrypted': config.is_encrypted
            })
        elif isinstance(config, InternalStorageConfig):
            data.update({
                'available_for_nova_gb': config.available_for_nova_gb,
                'cleanup_threshold_gb': config.cleanup_threshold_gb
            })
            
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    async def check_storage_health(self) -> Dict[str, any]:
        """Check storage health and available space"""
        health = {
            'status': 'healthy',
            'warnings': [],
            'internal_free_gb': 0,
            'external_free_gb': 0,
            'models_size_gb': 0,
            'memory_size_mb': 0
        }
        
        # Check internal storage
        internal_stat = shutil.disk_usage('/')
        health['internal_free_gb'] = round(internal_stat.free / (1024**3), 1)
        
        if health['internal_free_gb'] < 10:
            health['warnings'].append("Low internal storage (< 10GB free)")
            health['status'] = 'warning'
            
        # Check external storage if configured
        if self.config and self.config.use_external and self.config.external_path:
            try:
                external_stat = shutil.disk_usage(str(self.config.external_path))
                health['external_free_gb'] = round(external_stat.free / (1024**3), 1)
                
                if health['external_free_gb'] < 5:
                    health['warnings'].append("Low external storage (< 5GB free)")
                    health['status'] = 'warning'
            except:
                health['warnings'].append("External storage not accessible")
                health['status'] = 'error'
                
        # Check model storage usage
        models_size = await self._calculate_directory_size(self.config.models_path if self.config else self.dirs['models'])
        health['models_size_gb'] = round(models_size / (1024**3), 1)
        
        # Check memory usage
        memory_size = await self._calculate_directory_size(self.dirs['memory'])
        health['memory_size_mb'] = round(memory_size / (1024**2), 1)
        
        return health
        
    async def _calculate_directory_size(self, path: Path) -> int:
        """Calculate total size of a directory"""
        total_size = 0
        
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception as e:
            self.logger.error(f"Failed to calculate size for {path}: {e}")
            
        return total_size
        
    async def cleanup_temp_files(self) -> int:
        """Clean up temporary files"""
        cleaned = 0
        
        try:
            # Clean temp directory
            for item in self.dirs['temp'].iterdir():
                if item.is_file() and (datetime.now() - datetime.fromtimestamp(item.stat().st_mtime)).days > 1:
                    item.unlink()
                    cleaned += 1
                    
            # Clean old logs
            for log_file in self.dirs['logs'].glob('nova_*.log'):
                if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days > 7:
                    log_file.unlink()
                    cleaned += 1
                    
            self.logger.info(f"Cleaned {cleaned} temporary files")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            
        return cleaned
        
    async def suggest_cleanup(self) -> List[Dict[str, any]]:
        """Suggest files/models to clean up"""
        suggestions = []
        
        # Check model usage
        if self.config:
            # Get model usage stats from usage tracking
            usage_file = self.config.models_path / 'model_usage.json'
            if usage_file.exists():
                with open(usage_file, 'r') as f:
                    usage_data = json.load(f)
                    
                # Suggest removing unused models
                for model, stats in usage_data.items():
                    if stats.get('usage_count', 0) == 0:
                        suggestions.append({
                            'type': 'model',
                            'name': model,
                            'reason': 'Never used',
                            'size_gb': self._estimate_model_size(model)
                        })
                    elif stats.get('last_used'):
                        last_used = datetime.fromisoformat(stats['last_used'])
                        days_unused = (datetime.now() - last_used).days
                        if days_unused > 30:
                            suggestions.append({
                                'type': 'model',
                                'name': model,
                                'reason': f'Not used for {days_unused} days',
                                'size_gb': self._estimate_model_size(model)
                            })
                            
        # Check old conversation files
        old_conversations = 0
        for conv_file in (self.dirs['memory'] / 'conversations').glob('*.json'):
            if (datetime.now() - datetime.fromtimestamp(conv_file.stat().st_mtime)).days > 90:
                old_conversations += 1
                
        if old_conversations > 100:
            suggestions.append({
                'type': 'conversations',
                'name': 'Old conversations',
                'reason': f'{old_conversations} conversations older than 90 days',
                'size_mb': old_conversations * 0.1  # Estimate
            })
            
        return suggestions
        
    def _estimate_model_size(self, model_name: str) -> float:
        """Estimate model size in GB"""
        # Size estimates for common models
        size_map = {
            'llama3:70b': 40.0,
            'llama3:13b': 7.4,
            'llama3:8b': 4.7,
            'llama3:7b': 4.0,
            'codellama:34b': 19.0,
            'codellama:13b': 7.4,
            'codellama:7b': 3.8,
            'mistral:7b': 4.1,
            'mixtral:8x7b': 26.0,
            'phi3:medium': 2.7,
            'phi3:mini': 2.3,
            'tinyllama': 0.6,
            'gemma:7b': 5.0,
            'gemma:2b': 1.5
        }
        
        # Try exact match first
        if model_name in size_map:
            return size_map[model_name]
            
        # Try base model name
        base_name = model_name.split(':')[0] if ':' in model_name else model_name
        for key, size in size_map.items():
            if key.startswith(base_name):
                return size
                
        # Default estimate
        return 5.0
        
    async def migrate_to_external_storage(self, external_path: Path) -> bool:
        """Migrate models to external storage"""
        try:
            self.logger.info(f"Migrating models to {external_path}")
            
            # Create models directory on external drive
            external_models = external_path / 'models'
            external_models.mkdir(exist_ok=True)
            
            # Set environment variable for Ollama
            os.environ['OLLAMA_MODELS'] = str(external_models)
            
            # Copy existing models
            current_models = self.config.models_path if self.config else self.dirs['models']
            if current_models.exists() and current_models != external_models:
                self.logger.info("Copying existing models...")
                shutil.copytree(current_models, external_models, dirs_exist_ok=True)
                
                # Remove old models after successful copy
                shutil.rmtree(current_models)
                
            # Update configuration
            drive_stat = shutil.disk_usage(str(external_path))
            new_config = ExternalStorageConfig(
                use_external=True,
                external_path=external_path,
                internal_path=self.nova_home,
                strategy='maximum',
                prefer_cloud_apis=False,
                auto_cleanup=False,
                drive_name=external_path.name,
                drive_total_gb=round(drive_stat.total / (1024**3)),
                drive_available_gb=round(drive_stat.free / (1024**3)),
                drive_format='Unknown',
                is_encrypted=False
            )
            
            self.save_config(new_config)
            
            self.logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False
            
    def get_recommended_strategy(self, available_storage_gb: float, 
                               system_tier: str) -> str:
        """Get recommended storage strategy"""
        if available_storage_gb < 30:
            return 'minimal'
        elif available_storage_gb < 60 or system_tier == 'EFFICIENT':
            return 'balanced'
        else:
            return 'maximum'
    
    async def setup_storage(self, config: StorageConfig) -> bool:
        """Set up storage based on configuration"""
        try:
            # Create directory structure
            self.ensure_directories()
            
            # Save configuration
            self.save_config(config)
            
            # Initialize storage based on type
            if config.use_external:
                self.logger.info(f"Setting up external storage at {config.external_path}")
                if config.external_path:
                    config.external_path.mkdir(parents=True, exist_ok=True)
            else:
                self.logger.info(f"Setting up internal storage at {config.internal_path}")
                config.internal_path.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            self.logger.error(f"Storage setup failed: {e}")
            return False
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get current storage information"""
        try:
            config = self.load_config()
            
            # Get disk usage
            if config and config.use_external and config.external_path:
                storage_path = config.external_path
            else:
                storage_path = self.nova_home
                
            disk_usage = shutil.disk_usage(storage_path)
            
            return {
                'total_gb': disk_usage.total / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'used_gb': (disk_usage.total - disk_usage.free) / (1024**3),
                'storage_path': str(storage_path),
                'use_external': config.use_external if config else False,
                'strategy': config.strategy if config else 'balanced'
            }
        except Exception as e:
            self.logger.error(f"Failed to get storage info: {e}")
            return {
                'total_gb': 0,
                'free_gb': 0,
                'used_gb': 0,
                'storage_path': str(self.nova_home),
                'use_external': False,
                'strategy': 'balanced'
            }