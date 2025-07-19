from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime


@dataclass
class SystemSpecs:
    """Raw system specifications"""
    platform: str
    chip_type: str  # Intel, Apple Silicon
    chip_model: str  # Specific model like M1, M2 Pro
    cpu_cores: int
    cpu_frequency: float  # GHz
    ram_gb: int
    storage_gb: int
    storage_available_gb: int
    gpu_info: Optional[str]
    macos_version: str
    

@dataclass
class BenchmarkResults:
    """Performance benchmark results"""
    score: float
    cpu_score: float
    memory_score: float
    disk_score: float
    inference_speed: float  # tokens/sec
    timestamp: datetime
    

@dataclass 
class SystemProfile:
    """Analyzed system profile with capabilities"""
    chip_type: str  # Intel, M1, M2, M3, Future
    chip_generation: str 
    chip_year: int
    ram_gb: int
    storage_gb: int
    performance_tier: str  # ULTRA, PRO, EFFICIENT
    capabilities: Dict[str, bool]
    neural_engine: bool
    unified_memory: bool
    benchmark_results: Optional[BenchmarkResults]
    raw_specs: SystemSpecs
    
    @property
    def can_run_large_models(self) -> bool:
        """Check if system can run large models"""
        return self.performance_tier in ["ULTRA", "PRO"] and self.ram_gb >= 16
        
    @property
    def recommended_model_size(self) -> str:
        """Get recommended model size for this system"""
        if self.performance_tier == "ULTRA":
            return "70b"
        elif self.performance_tier == "PRO":
            return "13b" 
        else:
            return "7b"
            

@dataclass
class ConfigRecommendation:
    """System configuration recommendations"""
    performance_mode: str  # maximum, balanced, efficient
    model_strategy: str  # local_first, hybrid, cloud_first 
    storage_strategy: str  # internal, external, minimal
    recommended_models: list[str]
    max_model_size: str
    use_neural_engine: bool
    enable_background_tasks: bool
    memory_limit_mb: int