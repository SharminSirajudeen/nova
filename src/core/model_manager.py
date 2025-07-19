import os
import json
import subprocess
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import psutil

from ..models import Model, ModelType
from ..interfaces import IModelManager


@dataclass
class ModelUsageStats:
    """Usage statistics for a model"""
    usage_count: int = 0
    last_used: Optional[datetime] = None
    total_tokens: int = 0
    average_response_time: float = 0.0
    

class AdaptiveModelManager(IModelManager):
    """
    Manages AI models including selection, download, and lifecycle
    """
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.models_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger('NOVA.ModelManager')
        
        # Usage tracking
        self.usage_db_path = models_dir / 'model_usage.json'
        self.usage_data: Dict[str, ModelUsageStats] = self._load_usage_data()
        
        # Model registry  
        self.available_models: List[Model] = []
        self._refresh_available_models()
        
    def _load_usage_data(self) -> Dict[str, ModelUsageStats]:
        """Load model usage statistics"""
        if self.usage_db_path.exists():
            try:
                with open(self.usage_db_path, 'r') as f:
                    data = json.load(f)
                    
                # Convert to ModelUsageStats objects
                usage_stats = {}
                for model, stats in data.items():
                    usage_stats[model] = ModelUsageStats(
                        usage_count=stats.get('usage_count', 0),
                        last_used=datetime.fromisoformat(stats['last_used']) if stats.get('last_used') else None,
                        total_tokens=stats.get('total_tokens', 0),
                        average_response_time=stats.get('average_response_time', 0.0)
                    )
                return usage_stats
            except Exception as e:
                self.logger.error(f"Failed to load usage data: {e}")
                
        return {}
        
    def _save_usage_data(self):
        """Save model usage statistics"""
        data = {}
        for model, stats in self.usage_data.items():
            data[model] = {
                'usage_count': stats.usage_count,
                'last_used': stats.last_used.isoformat() if stats.last_used else None,
                'total_tokens': stats.total_tokens,
                'average_response_time': stats.average_response_time
            }
            
        with open(self.usage_db_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def discover_models(self):
        """Discover and return all available Ollama models"""
        self._refresh_available_models()
        return self.available_models
        
    def _refresh_available_models(self):
        """Refresh list of available models from Ollama"""
        self.available_models = []
        
        try:
            # Get list from Ollama
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output (skip header line)
            lines = result.stdout.strip().split('\n')[1:]
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        # Map to our Model objects
                        model = self._create_model_object(model_name)
                        if model:
                            self.available_models.append(model)
                            
        except subprocess.CalledProcessError:
            self.logger.error("Failed to list Ollama models")
        except FileNotFoundError:
            self.logger.error("Ollama not found. Please install Ollama first.")
            
    def _create_model_object(self, model_name: str) -> Optional[Model]:
        """Create Model object from model name"""
        self.logger.info(f"Creating model object for: {model_name}")
        
        # Model metadata
        model_info = {
            'llama3:70b': {
                'size_gb': 40.0, 'context': 8192, 'caps': ['general', 'code', 'reasoning'],
                'speed': 6, 'quality': 10
            },
            'llama3:13b': {
                'size_gb': 7.4, 'context': 4096, 'caps': ['general', 'code', 'reasoning'],
                'speed': 8, 'quality': 8  
            },
            'llama3:8b': {
                'size_gb': 4.7, 'context': 4096, 'caps': ['general', 'code'],
                'speed': 8, 'quality': 7
            },
            'llama3:7b': {
                'size_gb': 4.0, 'context': 4096, 'caps': ['general'],
                'speed': 9, 'quality': 7
            },
            'codellama:34b': {
                'size_gb': 19.0, 'context': 16384, 'caps': ['code', 'debugging'],
                'speed': 7, 'quality': 9
            },
            'codellama:13b': {
                'size_gb': 7.4, 'context': 16384, 'caps': ['code'],
                'speed': 8, 'quality': 8
            },
            'codellama:7b': {
                'size_gb': 3.8, 'context': 16384, 'caps': ['code'],
                'speed': 9, 'quality': 7
            },
            'mistral:7b': {
                'size_gb': 4.1, 'context': 8192, 'caps': ['general', 'fast'],
                'speed': 9, 'quality': 7
            },
            'mixtral:8x7b': {
                'size_gb': 26.0, 'context': 32768, 'caps': ['general', 'code', 'reasoning'],
                'speed': 7, 'quality': 9
            },
            'phi3:medium': {
                'size_gb': 2.7, 'context': 2048, 'caps': ['general', 'fast'],
                'speed': 9, 'quality': 6
            },
            'phi3:mini': {
                'size_gb': 2.3, 'context': 2048, 'caps': ['general', 'fast'],
                'speed': 10, 'quality': 5
            },
            'tinyllama': {
                'size_gb': 0.6, 'context': 2048, 'caps': ['basic'],
                'speed': 10, 'quality': 4
            },
            'gemma:7b': {
                'size_gb': 5.0, 'context': 8192, 'caps': ['general'],
                'speed': 8, 'quality': 7
            },
            'gemma:2b': {
                'size_gb': 1.5, 'context': 8192, 'caps': ['general', 'fast'],
                'speed': 10, 'quality': 5
            },
            # Dolphin models (uncensored)
            'tinydolphin:latest': {
                'size_gb': 0.636, 'context': 2048, 'caps': ['general', 'uncensored', 'fast'],
                'speed': 10, 'quality': 6
            },
            'tinydolphin': {  # Add without :latest tag
                'size_gb': 0.636, 'context': 2048, 'caps': ['general', 'uncensored', 'fast'],
                'speed': 10, 'quality': 6
            },
            'dolphin3:latest': {
                'size_gb': 4.9, 'context': 8192, 'caps': ['general', 'code', 'uncensored'],
                'speed': 9, 'quality': 9
            },
            'dolphin3': {  # Add without :latest tag
                'size_gb': 4.9, 'context': 8192, 'caps': ['general', 'code', 'uncensored'],
                'speed': 9, 'quality': 9
            },
            'dolphin-mistral': {
                'size_gb': 4.1, 'context': 8192, 'caps': ['general', 'code', 'uncensored', 'fast'],
                'speed': 10, 'quality': 8
            },
            'dolphin-mixtral': {
                'size_gb': 26, 'context': 32768, 'caps': ['general', 'code', 'uncensored', 'reasoning'],
                'speed': 7, 'quality': 10
            },
            'dolphin-qwen2': {
                'size_gb': 4.4, 'context': 8192, 'caps': ['code', 'uncensored', 'multilingual'],
                'speed': 9, 'quality': 8
            }
        }
        
        # Find matching model info
        # Try exact match first
        if model_name in model_info:
            self.logger.info(f"Found exact match for {model_name}")
            info = model_info[model_name]
            return Model(
                name=model_name,
                type=ModelType.LOCAL,
                size_gb=info['size_gb'],
                context_window=info['context'],
                capabilities=info['caps'],
                cost_per_1k_tokens=0.0,
                speed_score=info['speed'],
                quality_score=info['quality']
            )
        
        # Try without version tag (e.g., dolphin3:latest -> dolphin3)
        base_name = model_name.split(':')[0] if ':' in model_name else model_name
        self.logger.info(f"Trying base name: {base_name}")
        if base_name in model_info:
            self.logger.info(f"Found match for base name {base_name}")
            info = model_info[base_name]
            return Model(
                name=model_name,
                type=ModelType.LOCAL,
                size_gb=info['size_gb'],
                context_window=info['context'],
                capabilities=info['caps'],
                cost_per_1k_tokens=0.0,
                speed_score=info['speed'],
                quality_score=info['quality']
            )
            
        # Try partial match
        for key, info in model_info.items():
            if model_name.startswith(key.split(':')[0]):
                return Model(
                    name=model_name,
                    type=ModelType.LOCAL,
                    size_gb=info['size_gb'],
                    context_window=info['context'],
                    capabilities=info['caps'],
                    cost_per_1k_tokens=0.0,
                    speed_score=info['speed'],
                    quality_score=info['quality']
                )
                
        # Unknown model - create with defaults
        # This is NORMAL - we support ANY Ollama model
        self.logger.info(f"Creating generic model object for: {model_name}")
        return Model(
            name=model_name,
            type=ModelType.LOCAL,
            size_gb=5.0,  # Estimate
            context_window=4096,
            capabilities=['general', 'code'],  # Assume basic capabilities
            cost_per_1k_tokens=0.0,
            speed_score=7,
            quality_score=7  # Assume decent quality
        )
        
    async def download_model(self, model_name: str, progress_callback=None) -> bool:
        """Download a model with progress tracking"""
        try:
            self.logger.info(f"Downloading model: {model_name}")
            
            # Use subprocess for progress tracking
            process = await asyncio.create_subprocess_exec(
                'ollama', 'pull', model_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Read output for progress
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                line_text = line.decode().strip()
                if progress_callback and line_text:
                    progress_callback(line_text)
                    
            await process.wait()
            
            if process.returncode == 0:
                self.logger.info(f"Successfully downloaded: {model_name}")
                self._refresh_available_models()
                return True
            else:
                stderr = await process.stderr.read()
                self.logger.error(f"Failed to download {model_name}: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            return False
            
    async def download_models_parallel(self, model_names: List[str], max_concurrent: int = 3, progress_callback=None) -> Dict[str, bool]:
        """Download multiple models in parallel with retry logic"""
        results = {}
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_retry(model_name: str):
            async with semaphore:
                retry_count = 0
                max_retries = 3
                
                while retry_count < max_retries:
                    try:
                        # Add timeout to prevent hanging
                        process = await asyncio.create_subprocess_exec(
                            'ollama', 'pull', model_name,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        
                        try:
                            stdout, stderr = await asyncio.wait_for(
                                process.communicate(),
                                timeout=600  # 10 minutes
                            )
                            
                            if process.returncode == 0:
                                self.logger.info(f"Successfully downloaded: {model_name}")
                                results[model_name] = True
                                if progress_callback:
                                    progress_callback(f"✅ Completed: {model_name}")
                                return True
                            else:
                                retry_count += 1
                                if progress_callback:
                                    progress_callback(f"❌ Failed attempt {retry_count} for {model_name}")
                                
                        except asyncio.TimeoutError:
                            process.terminate()
                            await process.wait()
                            retry_count += 1
                            if progress_callback:
                                progress_callback(f"⏱️ Timeout attempt {retry_count} for {model_name}")
                            
                            # Clean up partial downloads
                            await self._cleanup_partial_downloads()
                            
                    except Exception as e:
                        self.logger.error(f"Error downloading {model_name}: {e}")
                        retry_count += 1
                    
                    if retry_count < max_retries:
                        await asyncio.sleep(10 * retry_count)  # Progressive backoff
                
                results[model_name] = False
                return False
        
        # Download all models in parallel
        tasks = [download_with_retry(name) for name in model_names]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self._refresh_available_models()
        return results
        
    async def _cleanup_partial_downloads(self):
        """Clean up stuck partial downloads"""
        models_path = Path.home() / '.ollama' / 'models' / 'blobs'
        if models_path.exists():
            partial_files = list(models_path.glob('*-partial*'))
            for f in partial_files:
                # Check if file hasn't been modified in 5 minutes
                if datetime.now().timestamp() - f.stat().st_mtime > 300:
                    try:
                        f.unlink()
                        self.logger.info(f"Cleaned up stuck file: {f.name[:40]}...")
                    except:
                        pass
            
    def get_available_models(self) -> List[Model]:
        """Get list of available models"""
        self._refresh_available_models()
        return self.available_models
        
    def select_model_for_task(self, task_type: str, complexity: str) -> Optional[Model]:
        """Select best model for a task"""
        if not self.available_models:
            return None
            
        # Filter by capability
        suitable_models = []
        
        if task_type == 'code_generation':
            suitable_models = [m for m in self.available_models if 'code' in m.capabilities]
        elif task_type == 'fast_response':
            suitable_models = [m for m in self.available_models if 'fast' in m.capabilities]
        else:
            suitable_models = [m for m in self.available_models if 'general' in m.capabilities]
            
        if not suitable_models:
            suitable_models = self.available_models
            
        # Sort by quality for complex tasks, speed for simple tasks
        if complexity == 'complex':
            suitable_models.sort(key=lambda m: m.quality_score, reverse=True)
        else:
            suitable_models.sort(key=lambda m: m.speed_score, reverse=True)
            
        return suitable_models[0] if suitable_models else None
        
    def track_usage(self, model_name: str, tokens: int, response_time: float):
        """Track model usage"""
        if model_name not in self.usage_data:
            self.usage_data[model_name] = ModelUsageStats()
            
        stats = self.usage_data[model_name]
        stats.usage_count += 1
        stats.last_used = datetime.now()
        stats.total_tokens += tokens
        
        # Update average response time
        if stats.average_response_time == 0:
            stats.average_response_time = response_time
        else:
            # Running average
            stats.average_response_time = (
                (stats.average_response_time * (stats.usage_count - 1) + response_time) 
                / stats.usage_count
            )
            
        self._save_usage_data()
        
    async def cleanup_unused_models(self, keep_days: int = 30) -> List[str]:
        """Remove models not used recently"""
        removed = []
        
        # Never remove if we only have one model
        if len(self.available_models) <= 1:
            return removed
            
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for model in self.available_models:
            if model.name in self.usage_data:
                stats = self.usage_data[model.name]
                if stats.last_used and stats.last_used < cutoff_date:
                    # Check if we should remove
                    if await self._should_remove_model(model):
                        if await self.remove_model(model.name):
                            removed.append(model.name)
                            
        return removed
        
    async def _should_remove_model(self, model: Model) -> bool:
        """Determine if a model should be removed"""
        # Check available storage
        storage_stat = shutil.disk_usage(self.models_dir)
        free_gb = storage_stat.free / (1024**3)
        
        # Remove if low on space and model is large
        if free_gb < 10 and model.size_gb > 5:
            return True
            
        # Keep at least one model of each type
        models_by_type = {}
        for m in self.available_models:
            for cap in m.capabilities:
                if cap not in models_by_type:
                    models_by_type[cap] = []
                models_by_type[cap].append(m)
                
        # Don't remove if it's the only model with a capability
        for cap in model.capabilities:
            if len(models_by_type.get(cap, [])) == 1:
                return False
                
        return True
        
    async def remove_model(self, model_name: str) -> bool:
        """Remove a model"""
        try:
            process = await asyncio.create_subprocess_exec(
                'ollama', 'rm', model_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            
            if process.returncode == 0:
                self.logger.info(f"Removed model: {model_name}")
                self._refresh_available_models()
                return True
            else:
                stderr = await process.stderr.read()
                self.logger.error(f"Failed to remove model: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing model: {e}")
            return False
            
    def get_usage_report(self) -> Dict[str, any]:
        """Get usage report for all models"""
        report = {
            'total_models': len(self.available_models),
            'total_usage': sum(s.usage_count for s in self.usage_data.values()),
            'models': []
        }
        
        for model in self.available_models:
            stats = self.usage_data.get(model.name, ModelUsageStats())
            
            model_report = {
                'name': model.name,
                'size_gb': model.size_gb,
                'usage_count': stats.usage_count,
                'last_used': stats.last_used.isoformat() if stats.last_used else 'Never',
                'average_response_time': round(stats.average_response_time, 2),
                'capabilities': model.capabilities
            }
            
            report['models'].append(model_report)
            
        # Sort by usage
        report['models'].sort(key=lambda m: m['usage_count'], reverse=True)
        
        return report
        
    def optimize_model_selection(self) -> List[str]:
        """Get recommendations for model optimization"""
        recommendations = []
        
        # Check usage patterns
        total_usage = sum(s.usage_count for s in self.usage_data.values())
        
        if total_usage > 0:
            # Find underused models
            for model in self.available_models:
                stats = self.usage_data.get(model.name, ModelUsageStats())
                usage_percent = (stats.usage_count / total_usage) * 100 if total_usage > 0 else 0
                
                if usage_percent < 1 and model.size_gb > 5:
                    recommendations.append(
                        f"Consider removing {model.name} - only {usage_percent:.1f}% of usage but takes {model.size_gb}GB"
                    )
                    
            # Find slow models
            for model_name, stats in self.usage_data.items():
                if stats.average_response_time > 10:
                    recommendations.append(
                        f"{model_name} is slow ({stats.average_response_time:.1f}s avg) - consider a faster model"
                    )
                    
        # Check if missing important models
        has_code_model = any('code' in m.capabilities for m in self.available_models)
        if not has_code_model:
            recommendations.append("No code-specific model found - consider adding codellama")
            
        return recommendations