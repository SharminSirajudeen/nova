import os
import subprocess
import time
import json
import logging
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import psutil

from ..interfaces import IAutomationLayer


@dataclass  
class CommandResult:
    """Result from terminal command execution"""
    success: bool
    output: str
    error: str
    return_code: int
    

@dataclass
class BrowserAction:
    """Browser automation action"""
    action_type: str  # navigate, click, fill, scroll, etc.
    target: str
    value: Optional[str] = None
    

@dataclass
class UIAction:
    """UI automation action"""
    action_type: str  # click, type, hotkey, etc.
    params: Dict[str, Any]
    

class MacAutomationLayer(IAutomationLayer):
    """
    Unified interface for controlling Mac through various automation methods
    Simplified version without complex dependencies
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.Automation')
        self._app_cache = {}
        
    async def execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute an automation action"""
        action_type = action.get('type')
        
        if action_type == 'applescript':
            result = await self.execute_applescript(action['script'])
            return result != "Error"
            
        elif action_type == 'terminal':
            result = await self.run_terminal_command(action['command'])
            return result.success
            
        elif action_type == 'open_url':
            return await self.open_url(action['url'])
            
        elif action_type == 'launch_app':
            return await self.launch_app(action['app_name'])
            
        elif action_type == 'file_operation':
            return await self.perform_file_operation(action['operation'])
            
        else:
            self.logger.warning(f"Unknown action type: {action_type}")
            return False
            
    async def execute_applescript(self, script: str) -> str:
        """
        Execute AppleScript and return result
        """
        try:
            # Write script to temporary file (handles complex scripts better)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.applescript', delete=False) as f:
                f.write(script)
                temp_path = f.name
                
            # Execute AppleScript
            process = await asyncio.create_subprocess_exec(
                'osascript', temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0
            )
            
            # Clean up
            os.unlink(temp_path)
            
            if process.returncode == 0:
                self.logger.info("AppleScript executed successfully")
                return stdout.decode().strip()
            else:
                self.logger.error(f"AppleScript error: {stderr.decode()}")
                return f"Error: {stderr.decode()}"
                
        except asyncio.TimeoutError:
            self.logger.error("AppleScript execution timed out")
            return "Error: Script execution timed out"
        except Exception as e:
            self.logger.error(f"AppleScript execution failed: {e}")
            return f"Error: {str(e)}"
            
    async def run_terminal_command(self, command: str, background: bool = False, 
                                 timeout: int = 60) -> CommandResult:
        """
        Execute terminal command with optional background execution
        """
        try:
            if background:
                # Run in background
                process = await asyncio.create_subprocess_shell(
                    f"nohup {command} > /tmp/nova_bg_$$.log 2>&1 &",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Give it a moment to start
                await asyncio.sleep(0.5)
                
                return CommandResult(
                    success=True,
                    output=f"Started background process",
                    error="",
                    return_code=0
                )
            else:
                # Run and wait for completion
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return CommandResult(
                    success=process.returncode == 0,
                    output=stdout.decode(),
                    error=stderr.decode(),
                    return_code=process.returncode
                )
                
        except asyncio.TimeoutError:
            return CommandResult(
                success=False,
                output="",
                error="Command execution timed out",
                return_code=-1
            )
        except Exception as e:
            return CommandResult(
                success=False,
                output="",
                error=str(e),
                return_code=-1
            )
            
    async def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            script = f'open location "{url}"'
            result = await self.execute_applescript(script)
            return not result.startswith("Error")
        except Exception as e:
            self.logger.error(f"Failed to open URL: {e}")
            return False
            
    async def launch_app(self, app_name: str, hidden: bool = False) -> bool:
        """Launch an application"""
        try:
            if hidden:
                script = f'tell application "{app_name}" to launch'
            else:
                script = f'tell application "{app_name}" to activate'
                
            result = await self.execute_applescript(script)
            self.logger.info(f"Launched {app_name}")
            return not result.startswith("Error")
            
        except Exception as e:
            self.logger.error(f"Failed to launch {app_name}: {e}")
            return False
            
    async def quit_app(self, app_name: str, force: bool = False) -> bool:
        """Quit an application"""
        try:
            if force:
                # Force quit
                result = await self.run_terminal_command(f"killall '{app_name}'")
                return result.success
            else:
                # Graceful quit
                script = f'tell application "{app_name}" to quit'
                result = await self.execute_applescript(script)
                return not result.startswith("Error")
                
        except Exception as e:
            self.logger.error(f"Failed to quit {app_name}: {e}")
            return False
            
    async def get_running_processes(self) -> List[Dict]:
        """Get list of running processes with details"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'],
                        'memory_percent': pinfo['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:20]  # Top 20 processes
        
    async def perform_file_operation(self, operation: Dict) -> bool:
        """Perform file system operations"""
        try:
            op_type = operation.get('type')
            
            if op_type == 'move':
                source = Path(operation['source'])
                destination = Path(operation['destination'])
                source.rename(destination)
                
            elif op_type == 'copy':
                import shutil
                source = Path(operation['source'])
                destination = Path(operation['destination'])
                if source.is_file():
                    shutil.copy2(source, destination)
                else:
                    shutil.copytree(source, destination)
                    
            elif op_type == 'delete':
                path = Path(operation['path'])
                if path.is_file():
                    path.unlink()
                else:
                    import shutil
                    shutil.rmtree(path)
                    
            elif op_type == 'create_directory':
                path = Path(operation['path'])
                path.mkdir(parents=True, exist_ok=True)
                
            elif op_type == 'organize':
                # Smart organization of files
                await self._organize_directory(operation['directory'])
                
            return True
            
        except Exception as e:
            self.logger.error(f"File operation failed: {e}")
            return False
            
    async def _organize_directory(self, directory: str):
        """Intelligently organize files in a directory"""
        dir_path = Path(directory)
        
        # Categories for organization
        categories = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.odt'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java'],
            'Data': ['.csv', '.json', '.xml', '.sql', '.db']
        }
        
        # Create category directories and move files
        for category, extensions in categories.items():
            category_dir = dir_path / category
            
            for ext in extensions:
                for file in dir_path.glob(f'*{ext}'):
                    if file.is_file() and file.parent == dir_path:
                        category_dir.mkdir(exist_ok=True)
                        file.rename(category_dir / file.name)
                        
        self.logger.info(f"Organized directory: {directory}")
        
    async def get_active_window_info(self) -> Dict:
        """Get information about the currently active window"""
        try:
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                set windowTitle to "N/A"
                
                try
                    tell process frontApp
                        set windowTitle to title of window 1
                    end tell
                end try
                
                return {frontApp, windowTitle}
            end tell
            '''
            
            result = await self.execute_applescript(script)
            if result and not result.startswith("Error"):
                parts = result.split(", ")
                return {
                    'app_name': parts[0] if parts else "Unknown",
                    'window_title': parts[1] if len(parts) > 1 else "N/A"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get active window info: {e}")
            
        return {'app_name': 'Unknown', 'window_title': 'N/A'}
        
    async def control_system_preferences(self, setting: str, value: Any) -> bool:
        """Control system preferences programmatically"""
        try:
            if setting == 'dark_mode':
                script = f'''
                tell application "System Events"
                    tell appearance preferences
                        set dark mode to {str(value).lower()}
                    end tell
                end tell
                '''
                result = await self.execute_applescript(script)
                return not result.startswith("Error")
                
            elif setting == 'volume':
                # Set system volume (0-100)
                script = f'set volume output volume {int(value)}'
                result = await self.execute_applescript(script)
                return not result.startswith("Error")
                
            else:
                self.logger.warning(f"Unknown system preference: {setting}")
                return False
                
        except Exception as e:
            self.logger.error(f"System preference control failed: {e}")
            return False
            
    async def get_system_info(self) -> Dict:
        """Get current system information"""
        try:
            # Get various system metrics
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'battery': psutil.sensors_battery()._asdict() if psutil.sensors_battery() else None,
                'active_window': await self.get_active_window_info()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}
            
    async def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot using macOS screencapture"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/nova_screenshot_{timestamp}.png"
            
        try:
            result = await self.run_terminal_command(f"screencapture -x {filename}")
            if result.success:
                self.logger.info(f"Screenshot saved to {filename}")
                return filename
            else:
                self.logger.error(f"Screenshot failed: {result.error}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return ""
            
    async def arrange_windows_for_task(self, task_type: str) -> bool:
        """Arrange windows optimally for different tasks"""
        try:
            if task_type == 'coding':
                # Simple side-by-side arrangement
                script = '''
                tell application "System Events"
                    -- Get screen dimensions
                    tell application "Finder"
                        set displayBounds to bounds of window of desktop
                        set screenWidth to item 3 of displayBounds
                        set screenHeight to item 4 of displayBounds
                    end tell
                    
                    -- Try to position code editor on left
                    set codeApps to {"Visual Studio Code", "Xcode", "Sublime Text"}
                    repeat with appName in codeApps
                        if exists (process appName) then
                            tell process appName
                                set frontmost to true
                                tell window 1
                                    set position to {0, 0}
                                    set size to {screenWidth / 2, screenHeight}
                                end tell
                            end tell
                            exit repeat
                        end if
                    end repeat
                end tell
                '''
                
            elif task_type == 'focus':
                # Hide all windows except the active one
                script = '''
                tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                    
                    repeat with appProcess in application processes
                        if name of appProcess is not frontApp and visible of appProcess is true then
                            set visible of appProcess to false
                        end if
                    end repeat
                end tell
                '''
                
            else:
                self.logger.warning(f"Unknown task type for window arrangement: {task_type}")
                return False
                
            result = await self.execute_applescript(script)
            return not result.startswith("Error")
            
        except Exception as e:
            self.logger.error(f"Window arrangement failed: {e}")
            return False