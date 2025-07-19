from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class StorageConfig:
    """Base storage configuration"""
    use_external: bool = False
    external_path: Optional[Path] = None
    internal_path: Path = Path.home() / ".nova"
    strategy: str = "balanced"  # minimal, balanced, maximum
    prefer_cloud_apis: bool = False
    auto_cleanup: bool = True
    min_free_space_gb: int = 10
    
    @property
    def models_path(self) -> Path:
        """Get path for model storage"""
        if self.use_external and self.external_path:
            return self.external_path / "models"
        return self.internal_path / "models"
        
    @property
    def memory_path(self) -> Path:
        """Get path for memory storage"""
        # Always use internal for memory
        return self.internal_path / "memory"
        

@dataclass
class ExternalStorageConfig(StorageConfig):
    """Configuration for external drive storage"""
    drive_name: str = ""
    drive_total_gb: int = 0
    drive_available_gb: int = 0
    drive_format: str = "APFS"  # APFS, HFS+, etc
    is_encrypted: bool = False
    
    def __post_init__(self):
        self.use_external = True
        self.strategy = "maximum"  # Use full capabilities with external
        

@dataclass
class InternalStorageConfig(StorageConfig):
    """Configuration for internal storage only"""
    available_for_nova_gb: int = 10  # How much we can use
    cleanup_threshold_gb: int = 5  # When to suggest cleanup
    
    def __post_init__(self):
        self.use_external = False
        self.prefer_cloud_apis = True  # Prefer cloud to save space
        self.auto_cleanup = True  # Auto cleanup old models