import subprocess
import platform
import psutil
import json
import time
import logging
import os
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
import asyncio
import re

from ..models import SystemProfile, SystemSpecs, BenchmarkResults, ConfigRecommendation
from ..interfaces import ISystemAnalyzer


class SmartSystemAnalyzer(ISystemAnalyzer):
    """
    NOVA uses intelligent ranges and capabilities detection
    Future-proof system analysis for any Mac
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.SystemAnalyzer')
        self._system_info_cache = None
        self._chip_cache = None
        
    async def analyze_mac(self) -> SystemProfile:
        """Analyze Mac hardware and create system profile"""
        specs = await self._get_system_specs()
        
        # Smart chip detection
        chip_info = self._analyze_chip(specs.chip_model)
        
        # Performance tier assignment
        performance_tier = self._determine_performance_tier(
            specs.ram_gb, 
            chip_info['performance_score']
        )
        
        # Capabilities detection
        capabilities = self._detect_capabilities(chip_info, specs)
        
        # Benchmark if unknown hardware
        benchmark_results = None
        if chip_info['is_unknown']:
            self.logger.info("Unknown chip detected, running benchmarks...")
            benchmark_results = await self._run_benchmarks()
            # Update performance score based on benchmarks
            chip_info['performance_score'] = self._score_from_benchmark(benchmark_results)
            
        profile = SystemProfile(
            chip_type=chip_info['type'],
            chip_generation=chip_info['generation'], 
            chip_year=chip_info['year'],
            ram_gb=specs.ram_gb,
            storage_gb=specs.storage_gb,
            performance_tier=performance_tier,
            capabilities=capabilities,
            neural_engine=chip_info['has_neural_engine'],
            unified_memory=chip_info['has_unified_memory'],
            benchmark_results=benchmark_results,
            raw_specs=specs
        )
        
        self.logger.info(f"System profile created: {performance_tier} tier on {chip_info['generation']}")
        return profile
        
    async def _get_system_specs(self) -> SystemSpecs:
        """Get raw system specifications"""
        # Get basic system info
        system_info = await self._get_system_info()
        
        # Parse CPU info
        cpu_info = self._parse_cpu_info(system_info)
        
        # Get memory and storage
        memory_gb = psutil.virtual_memory().total // (1024**3)
        disk_usage = psutil.disk_usage('/')
        storage_gb = disk_usage.total // (1024**3)
        storage_available_gb = disk_usage.free // (1024**3)
        
        return SystemSpecs(
            platform=platform.system(),
            chip_type=cpu_info['type'],
            chip_model=cpu_info['model'],
            cpu_cores=psutil.cpu_count(logical=False),
            cpu_frequency=psutil.cpu_freq().max / 1000 if psutil.cpu_freq() else 0,
            ram_gb=memory_gb,
            storage_gb=storage_gb,
            storage_available_gb=storage_available_gb,
            gpu_info=cpu_info.get('gpu'),
            macos_version=platform.mac_ver()[0]
        )
        
    async def _get_system_info(self) -> Dict:
        """Get system information using system_profiler"""
        if self._system_info_cache:
            return self._system_info_cache
            
        try:
            # Get hardware info
            hw_cmd = ['system_profiler', 'SPHardwareDataType', '-json']
            hw_result = await asyncio.create_subprocess_exec(
                *hw_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            hw_stdout, _ = await hw_result.communicate()
            hw_data = json.loads(hw_stdout.decode())['SPHardwareDataType'][0]
            
            # Get chip info if available
            chip_cmd = ['sysctl', '-n', 'machdep.cpu.brand_string']
            chip_result = await asyncio.create_subprocess_exec(
                *chip_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            chip_stdout, _ = await chip_result.communicate()
            chip_string = chip_stdout.decode().strip()
            
            self._system_info_cache = {
                'hardware': hw_data,
                'chip_string': chip_string
            }
            
            return self._system_info_cache
            
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}
            
    def _parse_cpu_info(self, system_info: Dict) -> Dict:
        """Parse CPU information from system info"""
        hw_data = system_info.get('hardware', {})
        chip_string = system_info.get('chip_string', '')
        
        # Detect chip type
        chip_type = 'Intel'
        chip_model = 'Unknown'
        
        if 'Apple' in chip_string or 'apple' in hw_data.get('cpu_type', '').lower():
            chip_type = 'Apple Silicon'
            
            # Extract model from chip string or hardware data
            if 'M1' in chip_string:
                chip_model = 'M1'
            elif 'M2' in chip_string:
                chip_model = 'M2'
            elif 'M3' in chip_string:
                chip_model = 'M3'
            elif 'M4' in chip_string:  # Future proofing
                chip_model = 'M4'
            else:
                # Try to extract from hardware data
                chip_name = hw_data.get('chip_type', '')
                if chip_name:
                    chip_model = chip_name
                    
        else:
            # Intel chip
            chip_model = chip_string.split()[0] if chip_string else 'Intel'
            
        return {
            'type': chip_type,
            'model': chip_model,
            'string': chip_string,
            'gpu': hw_data.get('graphics_card', None)
        }
        
    def _analyze_chip(self, chip_model: str) -> Dict:
        """Analyze chip capabilities and performance"""
        current_year = datetime.now().year
        
        # Known chip configurations
        known_chips = {
            'M1': {
                'generation': 'M1',
                'year': 2020,
                'performance_score': 5,
                'has_neural_engine': True,
                'has_unified_memory': True
            },
            'M2': {
                'generation': 'M2', 
                'year': 2022,
                'performance_score': 7,
                'has_neural_engine': True,
                'has_unified_memory': True
            },
            'M3': {
                'generation': 'M3',
                'year': 2023, 
                'performance_score': 9,
                'has_neural_engine': True,
                'has_unified_memory': True
            },
            'Intel': {
                'generation': 'Intel',
                'year': 2019,  # Approximate
                'performance_score': 3,
                'has_neural_engine': False,
                'has_unified_memory': False
            }
        }
        
        # Check if known chip
        for known_model, info in known_chips.items():
            if known_model in chip_model:
                return {
                    'type': 'Apple Silicon' if known_model != 'Intel' else 'Intel',
                    'generation': info['generation'],
                    'year': info['year'],
                    'performance_score': info['performance_score'],
                    'has_neural_engine': info['has_neural_engine'],
                    'has_unified_memory': info['has_unified_memory'],
                    'is_unknown': False
                }
                
        # Unknown chip - assume it's newer and powerful
        self.logger.info(f"Unknown chip detected: {chip_model}")
        
        # Extract year if possible
        year_match = re.search(r'20\d{2}', chip_model)
        chip_year = int(year_match.group()) if year_match else current_year
        
        # Future chips are assumed to be more powerful
        if chip_year > 2023:
            performance_score = 10
        else:
            performance_score = 5  # Conservative estimate
            
        return {
            'type': 'Apple Silicon' if 'Apple' in chip_model or 'M' in chip_model else 'Unknown',
            'generation': chip_model,
            'year': chip_year,
            'performance_score': performance_score,
            'has_neural_engine': 'Apple' in chip_model or chip_year > 2020,
            'has_unified_memory': 'Apple' in chip_model or chip_year > 2020,
            'is_unknown': True
        }
        
    def _determine_performance_tier(self, ram_gb: int, chip_score: int) -> str:
        """Determine performance tier based on RAM and chip score"""
        # ULTRA tier: High RAM and powerful chip
        if ram_gb >= 32 and chip_score >= 8:
            return "ULTRA"
        # PRO tier: Good RAM or powerful chip
        elif ram_gb >= 16 or chip_score >= 7:
            return "PRO"
        # EFFICIENT tier: Lower specs
        else:
            return "EFFICIENT"
            
    def _detect_capabilities(self, chip_info: Dict, specs: SystemSpecs) -> Dict[str, bool]:
        """Detect system capabilities"""
        capabilities = {
            'neural_engine': chip_info['has_neural_engine'],
            'unified_memory': chip_info['has_unified_memory'],
            'metal_support': chip_info['type'] != 'Intel',  # All Apple Silicon has Metal
            'accelerated_ml': chip_info['has_neural_engine'],
            'can_run_large_models': specs.ram_gb >= 16,
            'can_run_medium_models': specs.ram_gb >= 8,
            'has_dedicated_gpu': bool(specs.gpu_info and 'Radeon' in str(specs.gpu_info)),
            'supports_background_tasks': specs.cpu_cores >= 8,
            'fast_storage': True,  # Assume SSD on modern Macs
        }
        
        return capabilities
        
    async def _run_benchmarks(self) -> BenchmarkResults:
        """Run performance benchmarks for unknown hardware"""
        self.logger.info("Running performance benchmarks...")
        
        # CPU benchmark
        cpu_score = await self._benchmark_cpu()
        
        # Memory benchmark  
        memory_score = await self._benchmark_memory()
        
        # Disk benchmark
        disk_score = await self._benchmark_disk()
        
        # AI inference benchmark (simple test)
        inference_speed = await self._benchmark_inference()
        
        # Overall score
        overall_score = (cpu_score + memory_score + disk_score) / 3
        
        return BenchmarkResults(
            score=overall_score,
            cpu_score=cpu_score,
            memory_score=memory_score,
            disk_score=disk_score,
            inference_speed=inference_speed,
            timestamp=datetime.now()
        )
        
    async def _benchmark_cpu(self) -> float:
        """Simple CPU benchmark"""
        try:
            # Matrix multiplication benchmark
            import numpy as np
            
            size = 1000
            iterations = 10
            
            start = time.time()
            for _ in range(iterations):
                a = np.random.rand(size, size)
                b = np.random.rand(size, size)
                _ = np.dot(a, b)
            end = time.time()
            
            # Normalize score (10 = 1 second for test)
            elapsed = end - start
            score = min(10, 10 / elapsed)
            
            return round(score, 2)
            
        except Exception as e:
            self.logger.error(f"CPU benchmark failed: {e}")
            return 5.0  # Default middle score
            
    async def _benchmark_memory(self) -> float:
        """Simple memory benchmark"""
        try:
            # Memory bandwidth test
            size = 100 * 1024 * 1024  # 100MB
            iterations = 10
            
            data = bytearray(size)
            
            start = time.time()
            for _ in range(iterations):
                # Write
                for i in range(0, size, 4096):
                    data[i] = i % 256
                # Read
                total = sum(data[i] for i in range(0, size, 4096))
            end = time.time()
            
            # Normalize score
            elapsed = end - start
            score = min(10, 5 / elapsed)
            
            return round(score, 2)
            
        except Exception as e:
            self.logger.error(f"Memory benchmark failed: {e}")
            return 5.0
            
    async def _benchmark_disk(self) -> float:
        """Simple disk benchmark"""
        try:
            # Disk speed test
            import tempfile
            
            size = 50 * 1024 * 1024  # 50MB
            data = os.urandom(size)
            
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                # Write test
                start = time.time()
                tmp.write(data)
                tmp.flush()
                os.fsync(tmp.fileno())
                write_time = time.time() - start
                
                # Read test
                tmp.seek(0)
                start = time.time()
                _ = tmp.read()
                read_time = time.time() - start
                
            # Calculate speed in MB/s
            write_speed = (size / (1024 * 1024)) / write_time
            read_speed = (size / (1024 * 1024)) / read_time
            
            # Normalize score (500 MB/s = 10)
            avg_speed = (write_speed + read_speed) / 2
            score = min(10, avg_speed / 50)
            
            return round(score, 2)
            
        except Exception as e:
            self.logger.error(f"Disk benchmark failed: {e}")
            return 5.0
            
    async def _benchmark_inference(self) -> float:
        """Simple AI inference benchmark"""
        # For now, return estimate based on other scores
        # Real implementation would test with a small model
        return 100.0  # tokens/sec estimate
        
    def _score_from_benchmark(self, results: BenchmarkResults) -> int:
        """Convert benchmark results to performance score"""
        # Map benchmark score to 1-10 scale
        return min(10, int(results.score))
        
    async def benchmark_performance(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        benchmark_results = await self._run_benchmarks()
        return {
            'cpu_score': benchmark_results.cpu_score,
            'memory_score': benchmark_results.memory_score,
            'disk_score': benchmark_results.disk_score,
            'inference_score': benchmark_results.inference_speed,
            'overall_score': benchmark_results.overall_score
        }
    
    async def benchmark_system(self) -> float:
        """Public method to run benchmarks"""
        results = await self._run_benchmarks()
        return results.score
        
    def recommend_configuration(self, profile: SystemProfile) -> ConfigRecommendation:
        """Recommend optimal configuration for system"""
        # Performance mode based on tier
        if profile.performance_tier == "ULTRA":
            performance_mode = "maximum"
            memory_limit_mb = 16384  # 16GB
        elif profile.performance_tier == "PRO":
            performance_mode = "balanced"
            memory_limit_mb = 8192  # 8GB
        else:
            performance_mode = "efficient"
            memory_limit_mb = 4096  # 4GB
            
        # Model strategy
        if profile.ram_gb >= 32:
            model_strategy = "local_first"
            max_model_size = "70b"
        elif profile.ram_gb >= 16:
            model_strategy = "hybrid"
            max_model_size = "13b"
        else:
            model_strategy = "cloud_first"
            max_model_size = "7b"
            
        # Storage strategy
        if profile.storage_gb - (profile.raw_specs.storage_gb - profile.raw_specs.storage_available_gb) > 100:
            storage_strategy = "internal"
        else:
            storage_strategy = "minimal"
            
        # Recommended models based on capabilities
        recommended_models = self._recommend_models(profile)
        
        return ConfigRecommendation(
            performance_mode=performance_mode,
            model_strategy=model_strategy,
            storage_strategy=storage_strategy,
            recommended_models=recommended_models,
            max_model_size=max_model_size,
            use_neural_engine=profile.neural_engine,
            enable_background_tasks=profile.capabilities.get('supports_background_tasks', False),
            memory_limit_mb=memory_limit_mb
        )
        
    def _recommend_models(self, profile: SystemProfile) -> list[str]:
        """Recommend specific models for system"""
        if profile.performance_tier == "ULTRA":
            return [
                "llama3:70b",
                "codellama:34b",
                "mixtral:8x7b",
                "gemma:7b"  # Fast small model
            ]
        elif profile.performance_tier == "PRO":
            return [
                "llama3:13b",
                "codellama:13b",
                "mistral:7b",
                "phi3:medium"
            ]
        else:
            return [
                "llama3:7b",
                "phi3:mini",
                "tinyllama",
                "gemma:2b"
            ]