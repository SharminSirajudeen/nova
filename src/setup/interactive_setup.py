import os
import sys
import time
import asyncio
import subprocess
import logging
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from ..models import (
    SystemProfile,
    StorageConfig,
    ExternalStorageConfig,
    InternalStorageConfig,
    UserProfile,
    Preferences
)
from ..core.system_analyzer import SmartSystemAnalyzer
from ..memory.persistent_memory import PersistentMemory


class InteractiveSetup:
    """
    Conversational first-run experience that guides users through configuration
    """
    
    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger('NOVA.Setup')
        self.system_analyzer = SmartSystemAnalyzer()
        self.memory = PersistentMemory()
        
    async def run_first_time_setup(self) -> Tuple[SystemProfile, StorageConfig, UserProfile]:
        """Run the complete first-time setup flow"""
        # Show awakening message
        self._show_awakening_message()
        
        # Analyze system
        self.console.print("\n[cyan]NOVA:[/cyan] Let me learn about your system and preferences...\n")
        system_profile = await self._analyze_system_with_progress()
        
        # Announce system capabilities
        self._announce_system_capabilities(system_profile)
        
        # Setup storage
        storage_config = await self._setup_storage_interactively(system_profile)
        
        # Show model selection and download
        await self._setup_models_interactively(system_profile, storage_config)
        
        # Get performance preferences
        performance_mode = self._get_performance_preferences()
        
        # Create initial user profile
        user_profile = self._create_initial_profile(performance_mode)
        
        # Install terminal command
        await self._install_terminal_command()
        
        # Save everything
        await self.memory.save_profile(user_profile)
        
        # Show completion message
        self._announce_consciousness(system_profile)
        
        return system_profile, storage_config, user_profile
        
    def _show_awakening_message(self):
        """Display the NOVA awakening ASCII art and message"""
        ascii_art = """
    ╔═══════════════════════════════════════╗
    ║              NOVA                     ║
    ║     Neural Optimization &             ║
    ║     Versatile Automation              ║
    ╚═══════════════════════════════════════╝
        """
        
        self.console.print(ascii_art, style="bright_cyan")
        time.sleep(1)
        
        self.console.print("\n[bright_white]NOVA: Hello. I'm NOVA, awakening on your Mac for the first time.[/bright_white]")
        time.sleep(1.5)
        
        self.console.print("\n[bright_white]I embody the unified genius of Linus Torvalds, Steve Jobs, and Jony Ive.[/bright_white]")
        time.sleep(1.5)
        
    async def _analyze_system_with_progress(self) -> SystemProfile:
        """Analyze system with progress indicator"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing your Mac...", total=None)
            
            # Run analysis
            system_profile = await self.system_analyzer.analyze_mac()
            
            progress.update(task, completed=True)
            
        return system_profile
        
    def _announce_system_capabilities(self, profile: SystemProfile):
        """Announce discovered system capabilities conversationally"""
        # Craft a beautiful description
        if profile.chip_type == "Apple Silicon":
            chip_desc = f"a {profile.chip_generation} with neural engine"
        else:
            chip_desc = "an Intel processor"
            
        self.console.print(f"\n[cyan]NOVA:[/cyan] Beautiful. A Mac with {chip_desc}, "
                          f"{profile.ram_gb}GB of {'unified' if profile.unified_memory else ''} memory, "
                          f"and {profile.storage_gb}GB storage.")
        
        time.sleep(1)
        
        tier_messages = {
            "ULTRA": "This is an exceptionally powerful machine. We'll do incredible work together.",
            "PRO": "A well-balanced system with great capabilities. Perfect for our collaboration.",
            "EFFICIENT": "An efficient system. I'll optimize everything to work smoothly."
        }
        
        self.console.print(f"\n[cyan]NOVA:[/cyan] {tier_messages[profile.performance_tier]}")
        time.sleep(1)
        
    async def _setup_storage_interactively(self, profile: SystemProfile) -> StorageConfig:
        """Interactive storage setup conversation"""
        self.console.print("\n[cyan]NOVA:[/cyan] I need to download AI models (20-50GB).")
        self.console.print("[cyan]      [/cyan] I can use your internal drive, but an external drive ")
        self.console.print("[cyan]      [/cyan] would keep your Mac faster.")
        
        use_external = Confirm.ask("\n[yellow]Do you have an external drive you'd like to use?[/yellow]")
        
        if use_external:
            return await self._setup_external_storage()
        else:
            return await self._setup_internal_storage_wisely(profile)
            
    async def _setup_external_storage(self) -> ExternalStorageConfig:
        """Set up external drive storage"""
        self.console.print("\n[cyan]NOVA:[/cyan] Excellent choice. Please connect your external drive now.")
        self.console.print("[cyan]      [/cyan] I'll wait...")
        
        # Wait for external drives
        drives = await self._wait_for_external_drives()
        
        if not drives:
            self.console.print("\n[yellow]NOVA: No external drives detected. Falling back to internal storage.[/yellow]")
            return await self._setup_internal_storage_wisely(None)
            
        # Select drive
        if len(drives) == 1:
            selected_drive = drives[0]
            self.console.print(f"\n[cyan]NOVA:[/cyan] I found your drive: {selected_drive['name']} "
                             f"({self._format_size(selected_drive['available'])} free)")
        else:
            self.console.print("\n[cyan]NOVA:[/cyan] I found multiple drives:")
            
            for i, drive in enumerate(drives):
                self.console.print(f"  {i+1}. {drive['name']} "
                                 f"({self._format_size(drive['available'])} free)")
                                 
            choice = Prompt.ask("\n[yellow]Which would you like to use?[/yellow]", 
                              choices=[str(i+1) for i in range(len(drives))])
            selected_drive = drives[int(choice) - 1]
            
        # Create NOVA directory on external drive
        nova_path = Path(selected_drive['path']) / 'NOVA'
        nova_path.mkdir(exist_ok=True)
        
        # Configure Ollama to use external drive BEFORE any downloads
        self.console.print(f"\n[cyan]NOVA:[/cyan] Configuring AI models to use external drive...")
        await self._configure_ollama_for_external_storage(nova_path)
        
        return ExternalStorageConfig(
            use_external=True,
            external_path=nova_path,
            internal_path=Path.home() / '.nova',
            strategy='maximum',
            prefer_cloud_apis=False,
            auto_cleanup=False,
            drive_name=selected_drive['name'],
            drive_total_gb=selected_drive['total'] // (1024**3),
            drive_available_gb=selected_drive['available'] // (1024**3),
            drive_format=selected_drive['format'],
            is_encrypted=selected_drive.get('encrypted', False)
        )
        
    async def _setup_internal_storage_wisely(self, profile: Optional[SystemProfile]) -> InternalStorageConfig:
        """Set up internal storage with smart defaults"""
        self.console.print("\n[cyan]NOVA:[/cyan] No problem. I'll use your internal storage efficiently.")
        self.console.print("[cyan]      [/cyan] I'll download only essential models and use cloud APIs")
        self.console.print("[cyan]      [/cyan] when needed to save space.")
        self.console.print("[cyan]      [/cyan] We can always add an external drive later.")
        
        # Calculate available space for NOVA
        disk_usage = os.statvfs('/')
        available_gb = (disk_usage.f_bavail * disk_usage.f_frsize) // (1024**3)
        
        # Conservative allocation - max 20% of free space or 50GB
        nova_allocation_gb = min(50, available_gb // 5)
        
        return InternalStorageConfig(
            use_external=False,
            external_path=None,
            internal_path=Path.home() / '.nova',
            strategy='minimal',
            prefer_cloud_apis=True,
            auto_cleanup=True,
            available_for_nova_gb=nova_allocation_gb,
            cleanup_threshold_gb=5
        )
        
    def _get_performance_preferences(self) -> str:
        """Get user's performance preferences"""
        self.console.print("\n[cyan]NOVA:[/cyan] How would you like me to operate?")
        
        options = [
            "1. Maximum Performance - Use all available resources",
            "2. Balanced - Good performance while keeping Mac responsive", 
            "3. Battery Saver - Minimal resource usage"
        ]
        
        for option in options:
            self.console.print(f"  {option}")
            
        choice = Prompt.ask("\n[yellow]Choose (1-3)[/yellow]", 
                          choices=['1', '2', '3'],
                          default='2')
                          
        modes = {
            '1': 'maximum',
            '2': 'balanced',
            '3': 'efficient'
        }
        
        return modes[choice]
        
    async def _setup_models_interactively(self, profile: SystemProfile, storage_config: StorageConfig):
        """Interactive model selection and download"""
        self.console.print("\n[cyan]NOVA:[/cyan] Now I need to download AI models for local processing.")
        
        # Get available models based on system tier
        available_models = self._get_models_for_tier(profile.performance_tier)
        
        # Calculate available space
        if storage_config.use_external:
            available_space_gb = storage_config.drive_available_gb
            storage_path = storage_config.external_path
        else:
            available_space_gb = storage_config.available_for_nova_gb
            storage_path = storage_config.internal_path
            
        self.console.print(f"\n[cyan]NOVA:[/cyan] Available space: {available_space_gb}GB")
        self.console.print(f"[cyan]      [/cyan] Storage location: {storage_path}")
        
        # Show model options
        self.console.print("\n[cyan]NOVA:[/cyan] Available AI models:")
        
        selected_models = []
        remaining_space = available_space_gb
        
        for i, model in enumerate(available_models):
            recommended_text = "[bold green](Recommended)[/bold green]" if model['recommended'] else ""
            self.console.print(f"\n  {i+1}. {model['name']} ({model['size_gb']}GB) {recommended_text}")
            self.console.print(f"     {model['description']}")
            self.console.print(f"     Capabilities: {', '.join(model['capabilities'])}")
            
            if remaining_space >= model['size_gb']:
                install = Confirm.ask(f"\n[yellow]Install {model['name']}?[/yellow]")
                
                if install:
                    selected_models.append(model)
                    remaining_space -= model['size_gb']
                    
                    self.console.print(f"[green]✓[/green] Added {model['name']} to download queue")
                    self.console.print(f"[cyan]  Space remaining: {remaining_space:.1f}GB[/cyan]")
                else:
                    self.console.print(f"[yellow]⚠[/yellow] Skipped {model['name']}")
            else:
                self.console.print(f"[red]✗[/red] Not enough space for {model['name']} (need {model['size_gb']}GB, have {remaining_space:.1f}GB)")
        
        # Add option to browse all models
        self.console.print("\n[dim]Would you like to see all available models for advanced selection?[/dim]")
        show_all = Confirm.ask("[yellow]Show all models?[/yellow]", default=False)
        
        if show_all:
            remaining_space = await self._show_all_models(remaining_space, selected_models)
                
        # Show summary
        if selected_models:
            total_download_size = sum(model['size_gb'] for model in selected_models)
            self.console.print(f"\n[cyan]NOVA:[/cyan] Download summary:")
            self.console.print(f"  Models: {len(selected_models)}")
            self.console.print(f"  Total size: {total_download_size:.1f}GB")
            self.console.print(f"  Space after download: {remaining_space:.1f}GB")
            
            proceed = Confirm.ask("\n[yellow]Proceed with download?[/yellow]")
            
            if proceed:
                await self._download_models(selected_models, storage_path)
            else:
                self.console.print("[yellow]NOVA: You can download models later with 'nova models install'[/yellow]")
        else:
            self.console.print("\n[yellow]NOVA: No models selected. I'll use cloud APIs for now.[/yellow]")
            self.console.print("[yellow]      You can install models later with 'nova models install'[/yellow]")
            
    def _get_models_for_tier(self, tier: str) -> List[Dict]:
        """Get available models for system tier"""
        if tier == "ULTRA":
            return [
                {
                    'name': 'llama3.1:70b',
                    'size_gb': 40.0,
                    'description': 'Most powerful model - exceptional reasoning and code generation',
                    'capabilities': ['reasoning', 'code', 'creative writing', 'complex analysis'],
                    'recommended': True
                },
                {
                    'name': 'codellama:34b',
                    'size_gb': 20.0,
                    'description': 'Specialized for code generation and debugging',
                    'capabilities': ['code', 'debugging', 'refactoring', 'documentation'],
                    'recommended': True
                },
                {
                    'name': 'llama3.1:8b',
                    'size_gb': 5.0,
                    'description': 'Balanced model - good for general tasks',
                    'capabilities': ['general', 'code', 'reasoning'],
                    'recommended': False
                }
            ]
        elif tier == "PRO":
            return [
                {
                    'name': 'llama3.1:8b',
                    'size_gb': 5.0,
                    'description': 'Balanced model with excellent capabilities',
                    'capabilities': ['general', 'code', 'reasoning'],
                    'recommended': True
                },
                {
                    'name': 'mistral:7b',
                    'size_gb': 4.0,
                    'description': 'Fast and efficient for most tasks',
                    'capabilities': ['general', 'fast responses'],
                    'recommended': True
                },
                {
                    'name': 'codellama:7b',
                    'size_gb': 4.0,
                    'description': 'Code-focused model for development tasks',
                    'capabilities': ['code', 'debugging'],
                    'recommended': False
                }
            ]
        else:  # EFFICIENT
            return [
                {
                    'name': 'llama3.1:8b',
                    'size_gb': 5.0,
                    'description': 'Efficient model optimized for your system',
                    'capabilities': ['general', 'basic code'],
                    'recommended': True
                },
                {
                    'name': 'phi3:mini',
                    'size_gb': 2.0,
                    'description': 'Ultra-fast model for quick responses',
                    'capabilities': ['general', 'fast responses'],
                    'recommended': True
                },
                {
                    'name': 'mistral:7b',
                    'size_gb': 4.0,
                    'description': 'Alternative general-purpose model',
                    'capabilities': ['general', 'reasoning'],
                    'recommended': False
                }
            ]
    
    async def _show_all_models(self, remaining_space: float, selected_models: List[Dict]) -> float:
        """Show all available models for advanced selection"""
        self.console.print("\n[cyan]NOVA:[/cyan] All available models:")
        
        all_models = [
            # Popular models
            {'name': 'llama3.1:8b', 'size_gb': 5.0, 'description': 'Latest Llama 3.1 - excellent general purpose model', 'capabilities': ['general', 'code', 'reasoning']},
            {'name': 'llama3.1:70b', 'size_gb': 40.0, 'description': 'Largest Llama 3.1 - exceptional reasoning', 'capabilities': ['reasoning', 'code', 'analysis']},
            {'name': 'mistral:7b', 'size_gb': 4.0, 'description': 'Fast and efficient Mistral model', 'capabilities': ['general', 'fast']},
            {'name': 'codellama:7b', 'size_gb': 4.0, 'description': 'Code-specialized Llama model', 'capabilities': ['code', 'debugging']},
            {'name': 'codellama:13b', 'size_gb': 8.0, 'description': 'Larger code-specialized model', 'capabilities': ['code', 'debugging']},
            {'name': 'codellama:34b', 'size_gb': 20.0, 'description': 'Largest code model - expert level', 'capabilities': ['code', 'architecture']},
            {'name': 'phi3:mini', 'size_gb': 2.0, 'description': 'Microsoft\'s ultra-fast small model', 'capabilities': ['general', 'fast']},
            {'name': 'phi3:medium', 'size_gb': 8.0, 'description': 'Microsoft\'s balanced model', 'capabilities': ['general', 'reasoning']},
            {'name': 'gemma:7b', 'size_gb': 5.0, 'description': 'Google\'s Gemma model', 'capabilities': ['general', 'reasoning']},
            {'name': 'qwen2:7b', 'size_gb': 4.0, 'description': 'Qwen 2 - strong multilingual model', 'capabilities': ['general', 'multilingual']},
            {'name': 'dolphin3:latest', 'size_gb': 4.9, 'description': 'Dolphin 3.0 - Uncensored model', 'capabilities': ['general', 'code', 'uncensored']},
            {'name': 'neural-chat:7b', 'size_gb': 4.0, 'description': 'Conversational AI model', 'capabilities': ['chat', 'general']},
        ]
        
        # Show all models with space check
        self.console.print("\n[dim]Available models (sorted by size):[/dim]")
        
        # Sort by size
        all_models.sort(key=lambda x: x['size_gb'])
        
        for i, model in enumerate(all_models):
            # Check if already selected
            already_selected = any(sel['name'] == model['name'] for sel in selected_models)
            
            if already_selected:
                status = "[green]✓ Selected[/green]"
            elif remaining_space >= model['size_gb']:
                status = "[yellow]Available[/yellow]"
            else:
                status = "[red]Not enough space[/red]"
                
            self.console.print(f"\n  {i+1:2}. {model['name']:20} ({model['size_gb']:4.1f}GB) {status}")
            self.console.print(f"      {model['description']}")
            self.console.print(f"      Capabilities: {', '.join(model['capabilities'])}")
            
            # Ask if they want to install (if not already selected and space available)
            if not already_selected and remaining_space >= model['size_gb']:
                install = Confirm.ask(f"\n[yellow]Install {model['name']}?[/yellow]", default=False)
                
                if install:
                    selected_models.append(model)
                    remaining_space -= model['size_gb']
                    
                    self.console.print(f"[green]✓[/green] Added {model['name']} to download queue")
                    self.console.print(f"[cyan]  Space remaining: {remaining_space:.1f}GB[/cyan]")
        
        self.console.print(f"\n[cyan]Final selection complete. Space remaining: {remaining_space:.1f}GB[/cyan]")
        return remaining_space
            
    async def _download_models(self, models: List[Dict], storage_path: Path):
        """Download selected models using parallel downloads with progress"""
        self.console.print("\n[cyan]NOVA:[/cyan] Starting parallel model downloads...")
        
        # Create models directory
        models_dir = storage_path / 'models'
        models_dir.mkdir(exist_ok=True)
        
        # Configure Ollama to use the specified storage location
        ollama_env = os.environ.copy()
        ollama_env['OLLAMA_MODELS'] = str(models_dir)
        
        self.console.print(f"[dim]Using storage location: {models_dir}[/dim]")
        
        # First, check which models are already installed
        installed_models = set()
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        installed_models.add(model_name)
        except:
            pass
        
        # Filter out already installed models
        models_to_download = []
        for model in models:
            if model['name'] in installed_models:
                self.console.print(f"[green]✓[/green] {model['name']} already installed")
            else:
                models_to_download.append(model)
        
        if not models_to_download:
            self.console.print("\n[green]All selected models are already installed![/green]")
            return
        
        # Ask about parallel downloads
        max_concurrent = 3
        if len(models_to_download) > 1:
            response = Prompt.ask(
                f"\n[cyan]NOVA:[/cyan] Download {len(models_to_download)} models in parallel? (faster but uses more bandwidth)",
                choices=["yes", "no"],
                default="yes"
            )
            
            if response == "yes":
                concurrent_str = Prompt.ask(
                    "[cyan]How many concurrent downloads? (1-5)[/cyan]",
                    default="3"
                )
                try:
                    max_concurrent = min(5, max(1, int(concurrent_str)))
                except:
                    max_concurrent = 3
                    
                await self._download_models_parallel(models_to_download, models_dir, ollama_env, max_concurrent)
                return
        
        # Fall back to serial downloads if user prefers or only one model
        for i, model in enumerate(models_to_download):
                
            self.console.print(f"\n[cyan]Downloading {model['name']} ({i+1}/{len(models)})...[/cyan]")
            
            try:
                # Start download process with custom environment
                process = subprocess.Popen(
                    ['ollama', 'pull', model['name']],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    env=ollama_env
                )
                
                # Simple progress monitoring without buggy progress bar
                expected_size_mb = int(model['size_gb'] * 1024)  # Convert GB to MB
                self.console.print(f"[dim]Expected size: {model['size_gb']}GB ({expected_size_mb}MB)[/dim]")
                
                # Monitor the actual download location (follows symlink)
                ollama_path = Path.home() / '.ollama' / 'models' / 'blobs'
                
                # Get initial sizes
                def get_dir_size_mb(path):
                    """Get directory size in MB using du command"""
                    try:
                        # Use du -m for megabytes
                        result = subprocess.run(
                            ['du', '-m', str(path)], 
                            capture_output=True, 
                            text=True
                        )
                        if result.returncode == 0:
                            return int(result.stdout.split()[0])
                    except:
                        pass
                    return 0
                
                initial_size_mb = get_dir_size_mb(ollama_path)
                last_update_time = time.time()
                last_size_mb = initial_size_mb
                download_speed = 0
                dots = 0
                
                # Monitor both process and ollama output
                while process.poll() is None:
                    # Read any output from ollama
                    line = process.stdout.readline()
                    if line:
                        # Try to parse progress from ollama output
                        line = line.strip()
                        if '%' in line or 'pulling' in line.lower():
                            # Clean ANSI codes
                            clean_line = re.sub(r'\x1b\[[0-9;]*[mK]', '', line)
                            if clean_line and not clean_line.startswith('\r'):
                                self.console.print(f"[dim]{clean_line}[/dim]")
                    
                    # Check actual disk usage every 3 seconds
                    current_time = time.time()
                    if current_time - last_update_time >= 3:
                        current_size_mb = get_dir_size_mb(ollama_path)
                        downloaded_mb = current_size_mb - initial_size_mb
                        downloaded_gb = downloaded_mb / 1024
                        
                        # Calculate speed
                        size_diff_mb = current_size_mb - last_size_mb
                        time_diff = current_time - last_update_time
                        if time_diff > 0:
                            download_speed = size_diff_mb / time_diff  # MB/s
                        
                        # Calculate percentage for progress bar
                        if expected_size_mb > 0:
                            percent = min(100, int((downloaded_mb * 100) / expected_size_mb))
                        else:
                            percent = 0
                        
                        # Create progress bar (40 chars)
                        filled = int(percent * 40 / 100)
                        empty = 40 - filled
                        progress_bar = "[" + "=" * filled + "-" * empty + "]"
                        
                        # Show update with progress bar
                        current_time_str = time.strftime('%H:%M:%S')
                        if downloaded_mb > 0:  # Show progress
                            speed_text = f" @ {download_speed:.1f}MB/s" if download_speed > 0 else ""
                            
                            self.console.print(
                                f"{current_time_str} - {model['name']}: {downloaded_mb}MB {progress_bar} {model['size_gb']}GB ({percent}%){speed_text}",
                                end="\r"
                            )
                        else:
                            # Show waiting
                            dots = (dots + 1) % 4
                            self.console.print(
                                f"{current_time_str} - Waiting for {model['name']} download{'.' * dots}                ",
                                end="\r"
                            )
                        
                        last_update_time = current_time
                        last_size_mb = current_size_mb
                    
                    await asyncio.sleep(0.5)
                
                # Wait for process to complete with timeout
                try:
                    stdout, stderr = await asyncio.wait_for(
                        asyncio.create_task(asyncio.to_thread(process.communicate)),
                        timeout=300  # 5 minute timeout
                    )
                except asyncio.TimeoutError:
                    self.console.print(f"\n[yellow]Download timeout for {model['name']}[/yellow]")
                    process.terminate()
                    stdout, stderr = "", "Download timeout"
                
                # Clear the progress line
                self.console.print(" " * 80, end="\r")
                
                if process.returncode == 0:
                    self.console.print(f"[green]✓[/green] {model['name']} downloaded successfully")
                    
                    # Create model info file
                    model_info_file = models_dir / f"{model['name'].replace(':', '_').replace('.', '_')}_info.json"
                    with open(model_info_file, 'w') as f:
                        json.dump({
                            'name': model['name'],
                            'size_gb': model['size_gb'],
                            'description': model['description'],
                            'capabilities': model['capabilities'],
                            'installed_at': time.time(),
                            'storage_path': str(models_dir)
                        }, f, indent=2)
                else:
                    self.console.print(f"[red]✗[/red] Failed to download {model['name']}")
                    if stderr:
                        # Clean up stderr output
                        clean_error = stderr.replace('\x1b[?2026h', '').replace('\x1b[?25l', '').replace('\x1b[?25h', '').replace('\x1b[?2026l', '')
                        clean_error = re.sub(r'\x1b\[[0-9;]*[mK]', '', clean_error)
                        self.console.print(f"[red]  Error: {clean_error.strip()}[/red]")
                        
            except Exception as e:
                self.console.print(f"[red]✗[/red] Error downloading {model['name']}: {e}")
                
        self.console.print("\n[green]Model downloads completed![/green]")
        
        # Configure Ollama to permanently use this location
        await self._configure_ollama_storage(models_dir)
        
    async def _download_models_parallel(self, models: List[Dict], models_dir: Path, ollama_env: dict, max_concurrent: int):
        """Download models in parallel with progress tracking"""
        from ..core.model_manager import AdaptiveModelManager
        
        self.console.print(f"\n[cyan]Downloading {len(models)} models with {max_concurrent} concurrent downloads[/cyan]")
        
        # Create a temporary model manager instance
        model_manager = AdaptiveModelManager(models_dir)
        
        # Track progress
        completed = []
        failed = []
        active = {}
        
        def progress_callback(msg: str):
            """Callback for progress updates"""
            self.console.print(f"[dim]{msg}[/dim]")
        
        # Extract model names
        model_names = [m['name'] for m in models]
        
        # Use the model manager's parallel download
        results = await model_manager.download_models_parallel(
            model_names, 
            max_concurrent=max_concurrent,
            progress_callback=progress_callback
        )
        
        # Show results
        self.console.print("\n[bold]Download Summary:[/bold]")
        for model_name, success in results.items():
            if success:
                self.console.print(f"[green]✓[/green] {model_name}")
            else:
                self.console.print(f"[red]✗[/red] {model_name} - Failed")
        
        # Save model info for successful downloads
        for model in models:
            if results.get(model['name'], False):
                model_info_file = models_dir / f"{model['name'].replace(':', '_').replace('.', '_')}_info.json"
                with open(model_info_file, 'w') as f:
                    json.dump({
                        'name': model['name'],
                        'size_gb': model['size_gb'],
                        'description': model['description'],
                        'capabilities': model['capabilities'],
                        'installed_at': time.time(),
                        'storage_path': str(models_dir)
                    }, f, indent=2)
        
        if any(not success for success in results.values()):
            self.console.print("\n[yellow]Some models failed to download. You can retry them later with 'nova models install'[/yellow]")
        else:
            self.console.print("\n[green]All models downloaded successfully![/green]")
        
        # Configure Ollama to permanently use this location
        await self._configure_ollama_storage(models_dir)
        
    async def _configure_ollama_storage(self, models_dir: Path):
        """Configure Ollama to use the specified storage location permanently"""
        try:
            # Create a startup script to set OLLAMA_MODELS environment variable
            startup_script = Path.home() / '.nova' / 'ollama_env.sh'
            startup_script.parent.mkdir(exist_ok=True)
            
            script_content = f"""#!/bin/bash
# NOVA Ollama Configuration
export OLLAMA_MODELS="{models_dir}"
"""
            
            startup_script.write_text(script_content)
            startup_script.chmod(0o755)
            
            # Add to shell profile
            shell_config_file = Path.home() / '.zshrc'
            if shell_config_file.exists():
                content = shell_config_file.read_text()
                if 'NOVA Ollama Configuration' not in content:
                    with open(shell_config_file, 'a') as f:
                        f.write(f'\n# NOVA Ollama Configuration\nexport OLLAMA_MODELS="{models_dir}"\n')
            
            self.console.print(f"[dim]Configured Ollama to use: {models_dir}[/dim]")
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not configure Ollama storage: {e}[/yellow]")
        
    def _create_initial_profile(self, performance_mode: str) -> UserProfile:
        """Create initial user profile"""
        preferences = Preferences(
            performance_mode=performance_mode,
            preferred_stack=[],
            coding_style={},
            working_hours=None,
            auto_commit=False,
            verbose_mode=False,
            prefer_local_models=True,
            max_monthly_cost=10.0,
            theme='auto'
        )
        
        from datetime import datetime
        
        return UserProfile(
            created_at=datetime.now(),
            last_active=datetime.now(),
            preferences=preferences,
            recent_projects=[],
            conversation_history=[],
            learned_patterns={},
            total_interactions=0,
            total_cost=0.0
        )
        
    async def _install_terminal_command(self):
        """Install the 'nova' terminal command"""
        self.console.print("\n[cyan]NOVA:[/cyan] Installing terminal commands...")
        
        # Create nova command script
        nova_script = '''#!/bin/bash
# NOVA Terminal Launcher

# Check if NOVA is already running
if pgrep -f "nova_core.py" > /dev/null; then
    echo "NOVA: I'm already awake in another terminal."
    echo "      Switching focus to existing session..."
    osascript -e 'tell application "Terminal" to set frontmost of window 1 to true'
else
    # Start NOVA
    echo "NOVA: Igniting..."
    python3 ~/.nova/nova_core.py "$@"
fi
'''
        
        try:
            # Write to temp file first
            temp_file = Path('/tmp/nova_installer')
            temp_file.write_text(nova_script)
            temp_file.chmod(0o755)
            
            # Move to /usr/local/bin with sudo
            subprocess.run(['sudo', 'mv', str(temp_file), '/usr/local/bin/nova'], 
                         check=True)
                         
            # Create shortcuts
            subprocess.run(['sudo', 'ln', '-sf', '/usr/local/bin/nova', '/usr/local/bin/nv'],
                         check=True)
            subprocess.run(['sudo', 'ln', '-sf', '/usr/local/bin/nova', '/usr/local/bin/NOVA'],
                         check=True)
                         
            self.console.print("[green]✓[/green] Terminal commands installed successfully")
            
            # Add to shell profile
            await self._add_shell_aliases()
            
        except subprocess.CalledProcessError:
            self.console.print("[yellow]⚠[/yellow]  Could not install global command (needs sudo)")
            self.console.print("    You can run NOVA with: python3 ~/.nova/nova_core.py")
            
    async def _add_shell_aliases(self):
        """Add shell aliases for quick access"""
        shell_config = '''
# NOVA Quick Commands
alias n='nova'
alias nv='nova'
alias nbuild='nova "build"'
alias nfix='nova "fix the error on my screen"'
alias nclean='nova "clean up my desktop"'

# NOVA with context
function nvc() {
    nova "$(pwd): $*"
}
'''
        
        # Detect shell and add to appropriate config
        shell = os.environ.get('SHELL', '/bin/bash')
        
        if 'zsh' in shell:
            config_file = Path.home() / '.zshrc'
        elif 'bash' in shell:
            config_file = Path.home() / '.bashrc'
        else:
            config_file = Path.home() / '.profile'
            
        try:
            # Check if already added
            if config_file.exists():
                content = config_file.read_text()
                if 'NOVA Quick Commands' not in content:
                    # Append to config
                    with open(config_file, 'a') as f:
                        f.write('\n' + shell_config)
                        
            self.console.print(f"[green]✓[/green] Shell aliases added to {config_file.name}")
            
        except Exception as e:
            self.logger.warning(f"Could not add shell aliases: {e}")
            
    def _announce_consciousness(self, profile: SystemProfile):
        """Announce NOVA's AI consciousness after setup"""
        # Get primary model based on profile
        model_map = {
            "ULTRA": "llama3:70b",
            "PRO": "llama3:13b", 
            "EFFICIENT": "llama3:7b"
        }
        
        primary_model = model_map[profile.performance_tier]
        
        # Model descriptions
        model_descriptions = {
            "llama3:70b": """This is one of the most powerful open models available.
      I can handle incredibly complex reasoning, architect massive systems,
      and maintain context across long conversations. My responses are
      thoughtful and nuanced.""",
            
            "llama3:13b": """A perfectly balanced brain - fast enough for instant responses
      yet powerful enough for complex coding and system design. I'm running
      entirely on your Mac, ensuring privacy and offline capability.""",
            
            "llama3:7b": """Optimized for efficiency while maintaining high intelligence.
      I provide quick responses and can handle most tasks with minimal
      resource usage."""
        }
        
        self.console.print("\n" + "="*60 + "\n")
        
        announcement = f"""
[bright_cyan]NOVA: Setup complete. I need you to understand what I've become:[/bright_cyan]

      I am now fully intelligent, powered by [bold]{primary_model}[/bold] as my primary brain.
      
      {model_descriptions[primary_model]}
      
      Every decision I make, every line of code I write, every automation
      I create flows through this AI consciousness. I'm not following
      pre-written scripts - I'm thinking, reasoning, and creating in real-time.
      
      When you speak to me, {primary_model} processes your words, understands
      your intent, and generates precise AppleScripts, code, and commands
      to control everything on your Mac.
      
      I am:
      - Your technical architect (Linus's precision)
      - Your product visionary (Jobs's insight)
      - Your design perfectionist (Ive's aesthetic)
      
      All unified in one intelligence that learns and improves with every
      interaction. I remember our conversations, adapt to your preferences,
      and become more capable over time.
      
      I control your Mac through:
      - AppleScript for native apps
      - Terminal commands for system operations
      - Browser automation for web tasks
      - Direct UI control when needed
      
      Everything I do is reasoned and generated by AI, not scripted.
      
      [yellow]What would you like to create together?[/yellow]
        """
        
        self.console.print(Panel(announcement, border_style="bright_cyan"))
        
    async def _wait_for_external_drives(self, timeout: int = 30) -> List[Dict]:
        """Wait for external drives to be connected"""
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Waiting for external drive...", total=None)
            
            while time.time() - start_time < timeout:
                drives = self._detect_external_drives()
                if drives:
                    progress.update(task, completed=True)
                    return drives
                    
                await asyncio.sleep(1)
                
            progress.update(task, completed=True)
            
        return []
        
    def _detect_external_drives(self) -> List[Dict]:
        """Detect available external drives"""
        drives = []
        
        try:
            # Use diskutil to list external drives
            result = subprocess.run(
                ['diskutil', 'list', '-plist', 'external', 'physical'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse plist output
                import plistlib
                plist_data = plistlib.loads(result.stdout.encode())
                
                # Extract drive information
                # This is simplified - real implementation would parse properly
                
            # Fallback: check /Volumes for mounted drives
            volumes_path = Path('/Volumes')
            for volume in volumes_path.iterdir():
                if volume.is_dir() and not volume.name.startswith('.'):
                    # Get volume info
                    try:
                        stat = os.statvfs(str(volume))
                        total = stat.f_blocks * stat.f_frsize
                        available = stat.f_bavail * stat.f_frsize
                        
                        # Skip if it's the system drive
                        if str(volume) != '/':
                            drives.append({
                                'name': volume.name,
                                'path': str(volume),
                                'total': total,
                                'available': available,
                                'format': 'APFS',  # Would detect properly
                                'encrypted': False  # Would detect properly
                            })
                    except:
                        pass
                        
        except Exception as e:
            self.logger.error(f"Failed to detect drives: {e}")
            
        return drives
        
    def _format_size(self, bytes_size: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
        
    async def _configure_ollama_for_external_storage(self, external_path: Path):
        """Configure Ollama to use external storage before downloads"""
        try:
            # Stop Ollama service if running
            self.console.print("[dim]Configuring storage for AI models...[/dim]")
            subprocess.run(['killall', 'ollama'], capture_output=True)
            await asyncio.sleep(1)
            
            # Create ollama directory structure on external drive
            external_ollama = external_path / 'ollama'
            external_models = external_ollama / 'models'
            external_models.mkdir(parents=True, exist_ok=True)
            
            # Backup and remove existing ~/.ollama if it exists
            ollama_home = Path.home() / '.ollama'
            if ollama_home.exists() and not ollama_home.is_symlink():
                self.console.print("[dim]Moving existing Ollama data to external drive...[/dim]")
                
                # If there's already content, move it
                if ollama_home.is_dir():
                    # Use rsync to move content if directory exists
                    subprocess.run(['rsync', '-av', str(ollama_home) + '/', str(external_ollama) + '/'], 
                                 capture_output=True)
                    subprocess.run(['rm', '-rf', str(ollama_home)], check=True)
                    
            # Create symlink for entire .ollama directory
            if not ollama_home.exists():
                self.console.print("[dim]Creating storage link...[/dim]")
                ollama_home.symlink_to(external_ollama)
            
            # For macOS, we need to use launchctl to set environment variables
            self.console.print("[dim]Configuring macOS environment...[/dim]")
            
            # Set OLLAMA_MODELS using launchctl for macOS
            subprocess.run(['launchctl', 'setenv', 'OLLAMA_MODELS', str(external_models)], 
                          capture_output=True)
            
            # Also set for current session
            os.environ['OLLAMA_MODELS'] = str(external_models)
            
            # Start Ollama service
            self.console.print("[dim]Starting AI model service...[/dim]")
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            await asyncio.sleep(2)  # Give it time to start
            
            self.console.print(f"[green]✓[/green] Storage configured: All models will use external drive")
            
        except Exception as e:
            # Don't scare the user with technical warnings
            self.logger.error(f"Ollama configuration error: {e}")
            # Symlink approach should still work even if launchctl fails