#!/usr/bin/env python3
"""
NOVA Utility Functions - Common helpers and tools
"""

import os
import sys
import json
import yaml
import hashlib
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import re
import asyncio
import aiofiles
import logging
from functools import wraps, lru_cache
import time


class FileUtils:
    """File system utilities"""
    
    @staticmethod
    async def read_file_async(filepath: Union[str, Path]) -> str:
        """Read file asynchronously"""
        async with aiofiles.open(filepath, 'r') as f:
            return await f.read()
            
    @staticmethod
    async def write_file_async(filepath: Union[str, Path], content: str):
        """Write file asynchronously"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(content)
            
    @staticmethod
    def get_file_hash(filepath: Union[str, Path], algorithm: str = 'sha256') -> str:
        """Get hash of file contents"""
        hash_func = hashlib.new(algorithm)
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
                
        return hash_func.hexdigest()
        
    @staticmethod
    def find_files(pattern: str, directory: Union[str, Path] = '.') -> List[Path]:
        """Find files matching pattern"""
        directory = Path(directory)
        return list(directory.rglob(pattern))
        
    @staticmethod
    def safe_json_load(filepath: Union[str, Path], default: Any = None) -> Any:
        """Load JSON with error handling"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default
            
    @staticmethod
    def safe_yaml_load(filepath: Union[str, Path], default: Any = None) -> Any:
        """Load YAML with error handling"""
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError):
            return default
            
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    @staticmethod
    def get_size_formatted(size_bytes: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class ProcessUtils:
    """Process and system utilities"""
    
    @staticmethod
    async def run_command_async(cmd: List[str], 
                              timeout: Optional[float] = None) -> Tuple[int, str, str]:
        """Run command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            return process.returncode, stdout.decode(), stderr.decode()
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            raise TimeoutError(f"Command timed out: {' '.join(cmd)}")
            
    @staticmethod
    def run_command(cmd: List[str], timeout: Optional[float] = None) -> Tuple[int, str, str]:
        """Run command synchronously"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out: {' '.join(cmd)}")
            
    @staticmethod
    def is_process_running(name: str) -> bool:
        """Check if process is running by name"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', name],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
            
    @staticmethod
    def get_process_info(pid: int) -> Optional[Dict[str, Any]]:
        """Get process information"""
        try:
            import psutil
            process = psutil.Process(pid)
            return {
                'pid': pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'create_time': datetime.fromtimestamp(process.create_time())
            }
        except:
            return None


class TextUtils:
    """Text processing utilities"""
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown text"""
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        return [
            {
                'language': lang or 'plaintext',
                'code': code.strip()
            }
            for lang, code in matches
        ]
        
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, 
                     suffix: str = '...') -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
        
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text of extra whitespace"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
        
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.findall(url_pattern, text)
        
    @staticmethod
    def camel_to_snake(name: str) -> str:
        """Convert CamelCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
    @staticmethod
    def snake_to_camel(name: str) -> str:
        """Convert snake_case to CamelCase"""
        components = name.split('_')
        return ''.join(x.title() for x in components)


class TimeUtils:
    """Time and date utilities"""
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
            
    @staticmethod
    def parse_duration(duration_str: str) -> float:
        """Parse duration string to seconds"""
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([smhd])$', duration_str.lower())
        if not match:
            raise ValueError(f"Invalid duration format: {duration_str}")
            
        value, unit = match.groups()
        value = float(value)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        return value * multipliers[unit]
        
    @staticmethod
    def get_time_ago(timestamp: datetime) -> str:
        """Get human readable time ago"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 365:
            return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
        elif diff.days > 30:
            return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"


class CacheUtils:
    """Caching utilities"""
    
    @staticmethod
    def timed_cache(seconds: int):
        """Decorator for time-based caching"""
        def decorator(func):
            cache = {}
            cache_time = {}
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = str(args) + str(kwargs)
                now = time.time()
                
                if key in cache and now - cache_time[key] < seconds:
                    return cache[key]
                    
                result = func(*args, **kwargs)
                cache[key] = result
                cache_time[key] = now
                
                return result
                
            wrapper.clear_cache = lambda: (cache.clear(), cache_time.clear())
            return wrapper
            
        return decorator
        
    @staticmethod
    def async_timed_cache(seconds: int):
        """Decorator for async time-based caching"""
        def decorator(func):
            cache = {}
            cache_time = {}
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                key = str(args) + str(kwargs)
                now = time.time()
                
                if key in cache and now - cache_time[key] < seconds:
                    return cache[key]
                    
                result = await func(*args, **kwargs)
                cache[key] = result
                cache_time[key] = now
                
                return result
                
            wrapper.clear_cache = lambda: (cache.clear(), cache_time.clear())
            return wrapper
            
        return decorator


class ValidationUtils:
    """Input validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL"""
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return bool(re.match(pattern, url))
        
    @staticmethod
    def is_valid_path(path: str) -> bool:
        """Check if path is valid (not necessarily exists)"""
        try:
            Path(path)
            return True
        except:
            return False
            
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) > 31)
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        return filename


class SystemUtils:
    """System information utilities"""
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_system_info() -> Dict[str, Any]:
        """Get system information (cached)"""
        import platform
        
        info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node()
        }
        
        # macOS specific
        if info['platform'] == 'Darwin':
            try:
                result = subprocess.run(
                    ['system_profiler', 'SPHardwareDataType', '-json'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    hardware_data = json.loads(result.stdout)
                    info['hardware'] = hardware_data
            except:
                pass
                
        return info
        
    @staticmethod
    def get_available_memory() -> int:
        """Get available memory in bytes"""
        try:
            import psutil
            return psutil.virtual_memory().available
        except:
            # Fallback for macOS
            try:
                result = subprocess.run(
                    ['vm_stat'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    # Parse vm_stat output
                    for line in result.stdout.split('\n'):
                        if 'free' in line:
                            pages = int(line.split(':')[1].strip().rstrip('.'))
                            return pages * 4096  # Page size is 4096 bytes
            except:
                pass
            return 0
            
    @staticmethod
    def get_disk_usage(path: str = '/') -> Dict[str, int]:
        """Get disk usage statistics"""
        try:
            import psutil
            usage = psutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except:
            # Fallback using df
            try:
                result = subprocess.run(
                    ['df', '-k', path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 4:
                            total = int(parts[1]) * 1024
                            used = int(parts[2]) * 1024
                            free = int(parts[3]) * 1024
                            percent = (used / total * 100) if total > 0 else 0
                            return {
                                'total': total,
                                'used': used,
                                'free': free,
                                'percent': percent
                            }
            except:
                pass
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}


# Convenience functions
def retry_async(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for retrying async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                        
            raise last_exception
            
        return wrapper
    return decorator


def measure_time(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logging.debug(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper


def async_measure_time(func):
    """Decorator to measure async function execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logging.debug(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper