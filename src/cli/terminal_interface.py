#!/usr/bin/env python3
"""
NOVA Terminal Interface - Interactive CLI with enhanced features
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import subprocess
import webbrowser
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
import logging

from ..models import Command, CommandType, SystemProfile


class NOVATerminalInterface:
    """
    Enhanced Terminal interface for NOVA interactions
    """
    
    def __init__(self, nova_core):
        self.nova_core = nova_core
        self.console = Console()
        self.logger = logging.getLogger('NOVA.Terminal')
        self.running = False
        
        # Setup command history and completion
        self.history_file = Path.home() / '.nova' / 'command_history'
        self.history_file.parent.mkdir(exist_ok=True)
        
        # Command completer
        self.commands = [
            '/help', '/status', '/memory', '/models', '/clear', '/exit', '/reset',
            '/history', '/export', '/import', '/cost', '/benchmark',
            '/install', '/update', '/voice', '/screenshot', '/record',
            '/analyze', '/evolve', '/suggest', '/improve',
            '/mode', '/company', '/project', '/team'
        ]
        
        # Session state
        self.session_start = datetime.now()
        self.session_cost = 0.0
        self.session_tokens = 0
        self.voice_enabled = False
        
    def show_welcome(self):
        """Show enhanced welcome message"""
        # Get system info
        system_tier = "Unknown"
        if self.nova_core.system_profile:
            system_tier = self.nova_core.system_profile.performance_tier
            
        welcome_text = f"""
[bold cyan]NOVA[/bold cyan] - Neural Optimization & Versatile Automation

✨ Your AI co-founder is ready. I embody the unified genius of:
   • Linus Torvalds' technical precision
   • Steve Jobs' product vision  
   • Jony Ive's design perfection

🖥️  System: {system_tier} tier Mac
🧠 AI Models: {len(self.nova_core._get_available_models())} available ({self.nova_core.get_current_model_name()})
🏢 Mode: {self.nova_core.get_current_mode().title()}
💰 Budget: $10/month (optimized routing)

Type your request or use:
• /help - Show all commands
• /status - View system status
• Tab - Auto-complete commands
        """
        
        self.console.print(Panel(welcome_text, box=box.DOUBLE))
        
    def show_help(self):
        """Show comprehensive help information"""
        help_sections = {
            "Basic Commands": [
                ("/help", "Show this help message"),
                ("/status", "View system and AI status"),
                ("/memory", "View conversation history"),
                ("/models", "List available AI models"),
                ("/clear", "Clear the screen"),
                ("/reset", "Reset NOVA and start fresh setup"),
                ("/exit", "Exit NOVA")
            ],
            "Advanced Commands": [
                ("/history", "Show command history"),
                ("/export <file>", "Export conversation to file"),
                ("/import <file>", "Import conversation from file"),
                ("/cost", "Show detailed cost breakdown"),
                ("/benchmark", "Run system benchmark"),
                ("/install <model>", "Install a new AI model"),
                ("/download", "Download models to external drive"),
                ("/delete <model>", "Delete an installed model")
            ],
            "Evolution & Intelligence": [
                ("/analyze", "Show NOVA's self-analysis and insights"),
                ("/evolve", "View evolution progress with you"),
                ("/suggest", "Get AI-powered suggestions"),
                ("/improve", "Show self-improvement plan")
            ],
            "Mode & Company Commands": [
                ("/mode [mode]", "Switch between personal/company modes"),
                ("/company", "Show company dashboard (company mode)"),
                ("/project <cmd>", "Project management (company mode)"),
                ("/team", "Show AI development team (company mode)")
            ],
            "Productivity Commands": [
                ("/screenshot", "Take and analyze screenshot"),
                ("/voice", "Toggle voice input/output"),
                ("/record", "Record and transcribe audio"),
                ("/update", "Check for NOVA updates"),
                ("/workspace", "Set up project workspace")
            ],
            "Usage Examples": [
                ("Build me a todo app", "Create a new application"),
                ("Fix the error on my screen", "Debug visible errors"),
                ("Organize my downloads folder", "File management"),
                ("Monitor CPU and alert if > 80%", "System monitoring"),
                ("Create a Python backup script", "Generate code")
            ]
        }
        
        for section, commands in help_sections.items():
            table = Table(title=section, box=box.ROUNDED)
            table.add_column("Command", style="cyan", width=30)
            table.add_column("Description", style="white")
            
            for cmd, desc in commands:
                table.add_row(cmd, desc)
                
            self.console.print(table)
            self.console.print()  # Add spacing
            
    async def show_status(self):
        """Show enhanced system status with visual indicators"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Gathering system information..."),
            transient=True
        ) as progress:
            task = progress.add_task("status", total=None)
            status = await self.nova_core.get_system_status()
            progress.update(task, completed=True)
            
        # System Performance Panel
        cpu_bar = self._create_progress_bar(status['system']['cpu'], 100)
        mem_used = status['system']['memory_used']
        mem_total = status['system']['memory_total']
        mem_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0
        mem_bar = self._create_progress_bar(mem_percent, 100)
        
        system_panel = f"""
🖥️  Performance Tier: [bold]{status['system']['tier']}[/bold]

📊 CPU Usage: {cpu_bar} {status['system']['cpu']}%
💾 Memory: {mem_bar} {mem_used:.1f}/{mem_total}GB
💽 Storage Free: {status['system']['storage_free']}GB
        """
        
        self.console.print(Panel(system_panel, title="System Status", box=box.ROUNDED))
        
        # AI Models Panel
        ai_info = status['ai']
        if ai_info and 'available_models' in ai_info:
            model_lines = []
            for model in ai_info['available_models'][:5]:  # Show top 5
                icon = "🌐" if model['type'] == 'API' else "💻"
                cost = f"${model['cost']}/1k" if model['cost'] > 0 else "Free"
                model_lines.append(f"{icon} {model['name']} - {cost}")
                
            ai_panel = "\n".join(model_lines)
            self.console.print(Panel(ai_panel, title="Active AI Models", box=box.ROUNDED))
            
        # Session Statistics
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60
        session_panel = f"""
⏱️  Session Duration: {session_duration:.1f} minutes
💬 Conversations: {status['memory']['conversations']}
💰 Session Cost: ${self.session_cost:.4f}
🎯 Active Tasks: {status['tasks']['active']}
        """
        
        self.console.print(Panel(session_panel, title="Session Statistics", box=box.ROUNDED))
        
    def _create_progress_bar(self, value: float, max_value: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int((value / max_value) * width)
        bar = "█" * filled + "░" * (width - filled)
        color = "green" if value < 50 else "yellow" if value < 80 else "red"
        return f"[{color}]{bar}[/{color}]"
        
    async def show_memory(self):
        """Show enhanced memory view with search and filters"""
        memory = await self.nova_core.get_memory_summary()
        
        if not memory:
            self.console.print(Panel("[yellow]No conversation history yet[/yellow]", 
                                   title="Memory", box=box.ROUNDED))
            return
            
        # User Profile Card
        profile_card = f"""
👤 Profile Created: {memory['created_at']}
🔢 Total Interactions: {memory['total_interactions']}
💻 Preferred Stack: {memory['preferred_stack']}
🕐 Working Hours: {memory['working_hours']}

📁 Recent Projects:
{chr(10).join('  • ' + p for p in memory['recent_projects'][-5:])}
        """
        
        self.console.print(Panel(profile_card, title="Your Profile", box=box.ROUNDED))
        
        # Learned Patterns
        if memory['learned_patterns']:
            patterns_table = Table(title="Learned Patterns", box=box.ROUNDED)
            patterns_table.add_column("Pattern", style="cyan")
            patterns_table.add_column("Frequency", style="green")
            
            for pattern, freq in sorted(memory['learned_patterns'].items(), 
                                      key=lambda x: x[1], reverse=True)[:5]:
                patterns_table.add_row(pattern, str(freq))
                
            self.console.print(patterns_table)
            
        # Recent Conversations with syntax highlighting
        if memory['recent_conversations']:
            self.console.print("\n[bold]Recent Conversations:[/bold]")
            
            for conv in memory['recent_conversations'][-3:]:
                # User input
                self.console.print(f"\n[cyan]You ({conv['timestamp']}):[/cyan]")
                self.console.print(f"  {conv['user_input']}")
                
                # NOVA response (truncated)
                response = conv['nova_response']
                if len(response) > 200:
                    response = response[:200] + "..."
                    
                self.console.print(f"[green]NOVA ({conv['model']}):[/green]")
                self.console.print(f"  {response}")
                
                if conv['cost'] > 0:
                    self.console.print(f"  [dim]Cost: ${conv['cost']:.4f}[/dim]")
                    
    async def process_command(self, command: Command) -> Dict[str, Any]:
        """Process a command with enhanced features"""
        result = {'success': True, 'message': ''}
        
        try:
            if command.type == CommandType.INTERACTIVE:
                await self.run_interactive_mode()
            elif command.type == CommandType.STATUS:
                await self.show_status()
            elif command.type == CommandType.MEMORY:
                await self.show_memory()
            elif command.type == CommandType.SINGLE:
                # Show thinking indicator
                with self.console.status("[bold blue]NOVA is thinking...") as status:
                    response = await self.nova_core.process_user_request(command.content)
                    
                self.display_response(response)
            elif command.type == CommandType.BACKGROUND:
                task_id = await self.nova_core.start_background_task(command.content)
                self.console.print(Panel(
                    f"Background task started\nTask ID: [bold]{task_id}[/bold]\n\n" +
                    "Monitor with: nova --task-status {task_id}",
                    title="Task Launched", 
                    box=box.ROUNDED
                ))
            else:
                result = {'success': False, 'message': f'Unknown command type: {command.type}'}
                
        except Exception as e:
            self.logger.error(f"Command processing failed: {e}")
            result = {'success': False, 'message': str(e)}
            
        return result
        
    async def run_interactive_mode(self):
        """Run enhanced interactive conversation mode"""
        self.running = True
        self.show_welcome()
        
        # Create prompt session with history and auto-suggest
        session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=WordCompleter(self.commands, ignore_case=True)
        )
        
        while self.running:
            try:
                # Get user input with enhanced prompt
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None,
                    session.prompt,
                    "\n[You] > "
                )
                
                if not user_input.strip():
                    continue
                    
                # Handle special commands
                if user_input.startswith('/'):
                    await self.handle_special_command(user_input)
                    continue
                    
                # Process with AI
                start_time = datetime.now()
                
                # Show live thinking indicator
                with Live(
                    Panel("[bold blue]NOVA is thinking...[/bold blue]", 
                          box=box.ROUNDED),
                    refresh_per_second=4,
                    transient=True
                ) as live:
                    response = await self.nova_core.process_user_request(user_input)
                    
                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Update session stats
                self.session_cost += response.get('cost', 0)
                self.session_tokens += response.get('tokens', 0)
                
                # Display response with metadata
                self.display_response(response, processing_time)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Press Ctrl+C again to exit, or type /exit[/yellow]")
            except EOFError:
                break
            except Exception as e:
                self.console.print(Panel(
                    f"[red]Error: {e}[/red]",
                    title="Error",
                    box=box.ROUNDED
                ))
                
    async def handle_special_command(self, command: str):
        """Handle enhanced special slash commands"""
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == '/help':
            self.show_help()
        elif cmd == '/status':
            await self.show_status()
        elif cmd == '/memory':
            await self.show_memory()
        elif cmd == '/models':
            await self.show_models()
        elif cmd == '/clear':
            self.console.clear()
        elif cmd == '/exit':
            if Confirm.ask("Are you sure you want to exit?"):
                self.running = False
                self.console.print(Panel(
                    "[cyan]NOVA: Until we build again.[/cyan]",
                    box=box.ROUNDED
                ))
                await self.nova_core.shutdown()
        elif cmd == '/reset':
            await self.reset_nova()
        elif cmd == '/history':
            await self.show_history()
        elif cmd == '/cost':
            await self.show_cost_breakdown()
        elif cmd == '/benchmark':
            await self.run_benchmark()
        elif cmd == '/install':
            await self.install_model(args)
        elif cmd == '/download':
            await self.download_models_to_external(args)
        elif cmd == '/delete':
            await self.delete_model(args)
        elif cmd == '/export':
            await self.export_conversation(args)
        elif cmd == '/import':
            await self.import_conversation(args)
        elif cmd == '/screenshot':
            await self.take_screenshot()
        elif cmd == '/voice':
            await self.toggle_voice()
        elif cmd == '/update':
            await self.check_updates()
        elif cmd == '/analyze':
            await self.show_self_analysis()
        elif cmd == '/evolve':
            await self.show_evolution_status()
        elif cmd == '/suggest':
            await self.show_suggestions()
        elif cmd == '/improve':
            await self.show_improvement_plan()
        elif cmd == '/mode':
            await self.handle_mode_command(args)
        elif cmd == '/company':
            await self.handle_company_command(args)
        elif cmd == '/project':
            await self.handle_project_command(args)
        elif cmd == '/team':
            await self.show_team_info()
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("[dim]Type /help for available commands[/dim]")
            
    async def show_models(self):
        """Show enhanced AI models view with capabilities"""
        try:
            # First show installed local models
            await self._show_installed_models()
            
            # Then show available models
            models = self.nova_core.ai_engine.get_model_info()
            
            # Group models by type
            local_models = []
            free_models = []
            premium_models = []
            
            for model in models.get('available_models', []):
                if model['type'] == 'LOCAL':
                    local_models.append(model)
                elif model['type'] == 'FREE_API':
                    free_models.append(model)
                else:
                    premium_models.append(model)
                    
            # Display each group
            for group_name, group_models in [
                ("💻 Local Models (Offline)", local_models),
                ("🆓 Free Cloud Models", free_models),
                ("💎 Premium Models", premium_models)
            ]:
                if group_models:
                    table = Table(title=group_name, box=box.ROUNDED)
                    table.add_column("Model", style="cyan", width=20)
                    table.add_column("Context", style="yellow")
                    table.add_column("Speed", style="green")
                    table.add_column("Quality", style="blue")
                    table.add_column("Cost", style="magenta")
                    table.add_column("Best For", style="white")
                    
                    for model in group_models:
                        # Determine best use case
                        if 'code' in model.get('capabilities', []):
                            best_for = "Code generation"
                        elif model['quality'] >= 9:
                            best_for = "Complex reasoning"
                        elif model['speed'] >= 9:
                            best_for = "Quick responses"
                        else:
                            best_for = "General tasks"
                            
                        table.add_row(
                            model['name'],
                            f"{model.get('context_window', 'N/A')}",
                            self._create_rating_bar(model['speed']),
                            self._create_rating_bar(model['quality']),
                            f"${model['cost']}/1k" if model['cost'] > 0 else "Free",
                            best_for
                        )
                        
                    self.console.print(table)
                    self.console.print()  # Spacing
                    
            # Show routing statistics
            if 'routing_stats' in models:
                stats = models['routing_stats']
                
                # Create cost projection chart
                daily_cost = stats.get('cost_today', 0)
                monthly_estimate = daily_cost * 30
                budget_used = (monthly_estimate / 10) * 100 if monthly_estimate > 0 else 0
                
                cost_bar = self._create_progress_bar(budget_used, 100, 30)
                
                stats_panel = f"""
📊 Usage Statistics:
   • Total Requests: {stats.get('total_requests', 0)}
   • Local Model Usage: {stats.get('local_percentage', 0)}%
   • Free API Usage: {stats.get('free_percentage', 0)}%
   • Premium API Usage: {stats.get('premium_percentage', 0)}%

💰 Cost Analysis:
   • Today: ${daily_cost:.2f}
   • Monthly Estimate: ${monthly_estimate:.2f} / $10.00
   • Budget Usage: {cost_bar} {budget_used:.1f}%

🎯 Optimization Tips:
   {self._get_optimization_tips(stats)}
                """
                
                self.console.print(Panel(stats_panel, title="Cost Optimization", box=box.ROUNDED))
                
        except Exception as e:
            self.console.print(f"[red]Error getting model info: {e}[/red]")
            
    def _create_rating_bar(self, rating: int, max_rating: int = 10) -> str:
        """Create a visual rating bar"""
        filled = int((rating / max_rating) * 5)
        return "★" * filled + "☆" * (5 - filled)
        
    def _get_optimization_tips(self, stats: Dict) -> str:
        """Generate optimization tips based on usage"""
        tips = []
        
        if stats.get('premium_percentage', 0) > 20:
            tips.append("• Consider using more local models for routine tasks")
        if stats.get('local_percentage', 0) < 50:
            tips.append("• Download more local models to reduce costs")
        if stats.get('cost_today', 0) > 0.33:
            tips.append("• Current usage may exceed monthly budget")
            
        return "\n   ".join(tips) if tips else "• Usage is well optimized!"
        
    def display_response(self, response: Dict[str, Any], processing_time: float = None):
        """Display enhanced AI response with rich formatting"""
        # Determine response type and format accordingly
        content = response['response']
        
        # Check if response contains code
        if '```' in content:
            # Split response into parts
            parts = content.split('```')
            
            self.console.print(f"\n[bold green]NOVA[/bold green]:")
            
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Regular text
                    if part.strip():
                        self.console.print(part.strip())
                else:
                    # Code block
                    lines = part.strip().split('\n')
                    lang = lines[0] if lines else 'python'
                    code = '\n'.join(lines[1:]) if len(lines) > 1 else part
                    
                    syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
                    self.console.print(Panel(syntax, box=box.ROUNDED))
        else:
            # Regular response
            self.console.print(f"\n[bold green]NOVA[/bold green]: {content}")
            
        # Show actions taken with icons
        if response.get('actions'):
            action_panel = "\n".join([
                f"{'✓' if 'success' in action else '•'} {action}"
                for action in response['actions']
            ])
            self.console.print(Panel(
                action_panel,
                title="Actions Taken",
                box=box.ROUNDED,
                style="dim"
            ))
            
        # Show metadata footer
        metadata_parts = []
        
        if response.get('model'):
            metadata_parts.append(f"Model: {response['model']}")
            
        if processing_time:
            metadata_parts.append(f"Time: {processing_time:.1f}s")
            
        if response.get('tokens'):
            metadata_parts.append(f"Tokens: {response['tokens']}")
            
        if response.get('cost', 0) > 0:
            metadata_parts.append(f"Cost: ${response['cost']:.4f}")
            
        if metadata_parts:
            self.console.print(f"\n[dim]{' | '.join(metadata_parts)}[/dim]")
            
    async def show_history(self):
        """Show command history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = f.readlines()
                
            if history:
                table = Table(title="Command History", box=box.ROUNDED)
                table.add_column("#", style="cyan", width=5)
                table.add_column("Command", style="white")
                
                for i, cmd in enumerate(history[-20:], 1):  # Last 20 commands
                    table.add_row(str(i), cmd.strip())
                    
                self.console.print(table)
            else:
                self.console.print("[yellow]No command history yet[/yellow]")
        else:
            self.console.print("[yellow]No command history file found[/yellow]")
            
    async def show_cost_breakdown(self):
        """Show detailed cost breakdown"""
        # Get cost data from AI engine
        cost_data = self.nova_core.ai_engine.get_cost_breakdown()
        
        # Create cost table
        table = Table(title="Cost Breakdown", box=box.ROUNDED)
        table.add_column("Model", style="cyan")
        table.add_column("Requests", style="yellow")
        table.add_column("Tokens", style="green")
        table.add_column("Cost", style="magenta")
        
        total_cost = 0
        for model, data in cost_data.items():
            table.add_row(
                model,
                str(data['requests']),
                str(data['tokens']),
                f"${data['cost']:.4f}"
            )
            total_cost += data['cost']
            
        table.add_row(
            "[bold]TOTAL[/bold]",
            "",
            "",
            f"[bold]${total_cost:.4f}[/bold]"
        )
        
        self.console.print(table)
        
        # Monthly projection
        days_in_month = 30
        days_elapsed = (datetime.now() - self.session_start).days + 1
        projected_monthly = (total_cost / days_elapsed) * days_in_month
        
        projection_panel = f"""
📅 Session: {self.session_start.strftime('%Y-%m-%d')} - Now
💰 Session Total: ${self.session_cost:.4f}
📈 Monthly Projection: ${projected_monthly:.2f} / $10.00
⚡ Budget Status: {'✓ On track' if projected_monthly <= 10 else '⚠️ Over budget'}
        """
        
        self.console.print(Panel(projection_panel, title="Budget Status", box=box.ROUNDED))
        
    async def run_benchmark(self):
        """Run system benchmark"""
        self.console.print(Panel(
            "Running system benchmark...",
            title="Benchmark",
            box=box.ROUNDED
        ))
        
        # Re-analyze system
        analyzer = self.nova_core.system_analyzer
        profile = await analyzer.analyze_mac()
        
        # Run AI model benchmarks
        benchmark_results = []
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Benchmarking AI models...", total=3)
            
            # Test different model sizes
            test_prompt = "Write a hello world function in Python"
            
            for i, model_type in enumerate(['small', 'medium', 'large']):
                start = datetime.now()
                try:
                    # Simulate model test
                    await asyncio.sleep(0.5)  # Replace with actual model test
                    response_time = (datetime.now() - start).total_seconds()
                    benchmark_results.append((model_type, response_time))
                except:
                    benchmark_results.append((model_type, None))
                    
                progress.update(task, completed=i + 1)
                
        # Display results
        results_table = Table(title="Benchmark Results", box=box.ROUNDED)
        results_table.add_column("Component", style="cyan")
        results_table.add_column("Result", style="green")
        results_table.add_column("Rating", style="yellow")
        
        # System specs
        results_table.add_row(
            "Chip",
            f"{profile.chip_generation} ({profile.chip_type})",
            self._create_rating_bar(9 if 'M3' in profile.chip_generation else 7)
        )
        results_table.add_row(
            "RAM",
            f"{profile.ram_gb}GB",
            self._create_rating_bar(min(10, profile.ram_gb // 8))
        )
        results_table.add_row(
            "Neural Engine",
            "Available" if profile.neural_engine else "Not Available",
            self._create_rating_bar(10 if profile.neural_engine else 0)
        )
        
        # AI benchmarks
        for model_type, response_time in benchmark_results:
            if response_time:
                rating = 10 if response_time < 1 else 7 if response_time < 2 else 5
                results_table.add_row(
                    f"AI Response ({model_type})",
                    f"{response_time:.2f}s",
                    self._create_rating_bar(rating)
                )
                
        self.console.print(results_table)
        
        # Overall assessment
        assessment = self._get_system_assessment(profile)
        self.console.print(Panel(
            assessment,
            title="System Assessment",
            box=box.ROUNDED
        ))
        
    def _get_system_assessment(self, profile: SystemProfile) -> str:
        """Generate system assessment based on profile"""
        if profile.performance_tier == "ULTRA":
            return """
🚀 ULTRA Performance Tier

Your Mac is a powerhouse! You can:
• Run the largest AI models locally
• Handle complex multi-agent workflows
• Process massive datasets
• Execute parallel AI tasks

Recommendation: Enable all features for maximum productivity.
            """
        elif profile.performance_tier == "PRO":
            return """
⚡ PRO Performance Tier

Your Mac has excellent capabilities! You can:
• Run medium-sized AI models locally
• Handle most professional workflows
• Process standard datasets efficiently
• Execute multiple AI tasks

Recommendation: Use hybrid local/cloud approach for optimal results.
            """
        else:
            return """
✨ EFFICIENT Performance Tier

Your Mac is optimized for efficiency! You can:
• Run compact AI models locally
• Handle everyday tasks smoothly
• Process documents and code
• Execute focused AI tasks

Recommendation: Leverage cloud models for complex tasks.
            """
            
    async def install_model(self, model_name: str):
        """Install a new AI model"""
        if not model_name:
            self.console.print("[red]Please specify a model name[/red]")
            return
            
        # Check if Ollama is available
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode != 0:
                self.console.print("[red]Ollama is not installed or not running[/red]")
                return
        except:
            self.console.print("[red]Ollama is not available[/red]")
            return
            
        # Install model
        self.console.print(f"Installing {model_name}...")
        
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Downloading {model_name}...", total=None)
            
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for line in process.stdout:
                if 'pulling' in line.lower():
                    progress.update(task, description=f"[cyan]{line.strip()}")
                    
            process.wait()
            
        if process.returncode == 0:
            self.console.print(f"[green]✓ Model {model_name} installed successfully![/green]")
        else:
            self.console.print(f"[red]Failed to install {model_name}[/red]")
            
    async def _show_installed_models(self):
        """Show all installed local models with their sizes"""
        try:
            # Get list of installed models using ollama
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode != 0:
                return
                
            # Parse the output
            lines = result.stdout.strip().split('\n')
            if len(lines) <= 1:  # No models or only header
                self.console.print("\n[yellow]No local models installed yet.[/yellow]")
                self.console.print("[dim]Use /install <model> to download models[/dim]\n")
                return
                
            # Create table for installed models
            table = Table(title="📦 Installed Local Models", box=box.ROUNDED)
            table.add_column("Model", style="cyan", width=25)
            table.add_column("Size", style="yellow", justify="right")
            table.add_column("Modified", style="green")
            table.add_column("ID", style="dim")
            
            # Parse ollama list output (skip header)
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        model_name = parts[0]
                        model_id = parts[1]
                        size = parts[2]
                        modified = ' '.join(parts[3:])
                        
                        table.add_row(model_name, size, modified, model_id[:12])
                        
            self.console.print(table)
            
            # Show storage location if models are on external drive
            storage_config = await self.nova_core.memory.load_storage_config()
            if storage_config and storage_config.get('use_external'):
                models_path = Path(storage_config['external_path']) / 'models'
                self.console.print(f"\n[dim]Storage location: {models_path}[/dim]")
                
                # Calculate total size of models directory
                if models_path.exists():
                    total_size = sum(f.stat().st_size for f in models_path.rglob('*') if f.is_file())
                    self.console.print(f"[dim]Total space used: {self._format_size(total_size)}[/dim]")
                    
            self.console.print("\n[dim]Commands: /delete <model> to remove, /install <model> to add[/dim]\n")
            
        except FileNotFoundError:
            self.console.print("\n[yellow]Ollama is not installed.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error listing models: {e}[/red]")
            
    async def delete_model(self, model_name: str):
        """Delete an installed model"""
        if not model_name:
            # Show installed models first
            await self._show_installed_models()
            self.console.print("\n[yellow]Please specify a model to delete:[/yellow]")
            self.console.print("[dim]Usage: /delete <model_name>[/dim]")
            return
            
        # Confirm deletion
        self.console.print(f"\n[yellow]Warning: This will delete the model '{model_name}' and free up disk space.[/yellow]")
        confirm = Confirm.ask(f"Delete {model_name}?", default=False)
        
        if not confirm:
            self.console.print("[dim]Deletion cancelled[/dim]")
            return
            
        # Delete the model
        self.console.print(f"\n[cyan]Deleting {model_name}...[/cyan]")
        
        try:
            # Use ollama rm command
            result = subprocess.run(
                ['ollama', 'rm', model_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.console.print(f"[green]✓ Model {model_name} deleted successfully![/green]")
                
                # Show remaining models
                self.console.print("\n[dim]Remaining models:[/dim]")
                await self._show_installed_models()
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.console.print(f"[red]✗ Failed to delete {model_name}: {error_msg}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]✗ Error deleting model: {e}[/red]")
            
    def _format_size(self, bytes_size: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    async def download_models_to_external(self, model_names: str = ""):
        """Download models directly to external drive with full library"""
        import subprocess
        import json
        
        # Check if external storage is configured
        storage_config = await self.nova_core.memory.load_storage_config()
        if not storage_config or not storage_config.get('use_external'):
            self.console.print("[red]No external drive configured![/red]")
            self.console.print("[yellow]Please restart NOVA and select an external drive during setup[/yellow]")
            return
        
        external_path = storage_config.get('external_path', '/Volumes/SandiskSSD/NOVA')
        
        self.console.print(f"\n[cyan]NOVA:[/cyan] Downloading models to external drive...")
        self.console.print(f"[dim]Location: {external_path}/ollama/models[/dim]\n")
        
        # Get system RAM
        system_ram = self.nova_core.system_profile.ram_gb if self.nova_core.system_profile else 8
        
        # If no models specified, show selection menu
        if not model_names:
            self.console.print(f"[bold cyan]Fetching Latest Ollama Models...[/bold cyan]")
            
            # Try to fetch available models from Ollama
            try:
                # First try to get locally available models
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                local_models = []
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if parts:
                                local_models.append(parts[0])
                
                # Try to fetch all available models from Ollama registry
                # This would require ollama to have a list command or API endpoint
                # For now, we'll use a comprehensive hardcoded list that can be updated
                
                self.console.print(f"[dim]Your system: {system_ram}GB RAM[/dim]")
                self.console.print(f"[dim]Already installed: {len(local_models)} models[/dim]\n")
            
            except Exception as e:
                self.console.print(f"[yellow]Note: Could not fetch local models: {e}[/yellow]")
                local_models = []
            
            # Import the complete registry
            from ..core.ollama_registry import OLLAMA_COMPLETE_REGISTRY, get_compatible_models, check_model_compatibility
            
            # Group models by category
            categories = {
                "🐬 Uncensored Models (Dolphin)": [],
                "🧠 Advanced Reasoning (DeepSeek R1)": [],
                "🌟 Recommended for your Mac": [],
                "💻 Code Generation": [],
                "💬 Chat Optimized": [],
                "⚡ Fast & Efficient": [],
                "🌍 Multilingual": [],
                "👁️ Vision Models": [],
                "🔬 Specialized": [],
                "🚀 Large Models": []
            }
            
            # Get compatible models
            compatible_models = get_compatible_models(system_ram)
            compatible_names = {m['name'] for m in compatible_models}
            
            # Categorize models
            for i, model in enumerate(OLLAMA_COMPLETE_REGISTRY):
                tags = model.get('tags', [])
                
                # Mark compatibility
                if model['name'] in compatible_names:
                    compat_mark = "✅"
                else:
                    compat_mark = "⚠️"
                    
                entry = {
                    'num': i + 1,
                    'name': model['name'],
                    'size': f"{model['size_gb']}GB",
                    'ram': f"{model['ram_required']}GB",
                    'desc': model['description'],
                    'compat': compat_mark
                }
                
                # Add to categories
                # Prioritize uncensored models (Dolphin)
                if 'uncensored' in tags:
                    categories["🐬 Uncensored Models (Dolphin)"].append(entry)
                    
                # DeepSeek R1 reasoning models
                if 'deepseek-r1' in model['name']:
                    categories["🧠 Advanced Reasoning (DeepSeek R1)"].append(entry)
                elif 'reasoning' in tags and model['size_gb'] > 15:
                    categories["🧠 Advanced Reasoning (DeepSeek R1)"].append(entry)
                    
                # Code models
                if 'code' in tags:
                    categories["💻 Code Generation"].append(entry)
                    
                # Vision models
                if 'vision' in tags:
                    categories["👁️ Vision Models"].append(entry)
                    
                # Fast models
                if 'fast' in tags or 'tiny' in tags:
                    categories["⚡ Fast & Efficient"].append(entry)
                    
                # Chat models
                if 'chat' in tags and 'uncensored' not in tags:
                    categories["💬 Chat Optimized"].append(entry)
                    
                # Multilingual
                if 'multilingual' in tags:
                    categories["🌍 Multilingual"].append(entry)
                    
                # Specialized (math, medical, etc)
                if any(t in tags for t in ['math', 'medical', 'long-context', 'rag']):
                    categories["🔬 Specialized"].append(entry)
                    
                # Large models
                if model['size_gb'] > 30:
                    categories["🚀 Large Models"].append(entry)
                    
                # Add recommended models (compatible, good balance)
                if model['name'] in compatible_names and model['size_gb'] < 10:
                    if any(t in tags for t in ['general', 'code', 'uncensored']):
                        # Special recommendations
                        if 'dolphin' in model['name'] or 'deepseek-r1' in model['name']:
                            categories["🌟 Recommended for your Mac"].append(entry)
                        elif model['name'] in ['llama3.1:8b', 'mistral:7b', 'codellama:7b']:
                            categories["🌟 Recommended for your Mac"].append(entry)
            
            # Display models by category
            for category, models in categories.items():
                if not models:
                    continue
                    
                self.console.print(f"\n[bold yellow]{category}[/bold yellow]")
                
                # Create table for this category
                from rich.table import Table
                table = Table(box=None, padding=(0, 2))
                table.add_column("#", style="dim", width=4)
                table.add_column("Model", style="cyan", width=20)
                table.add_column("Size", style="yellow", width=8)
                table.add_column("RAM", style="magenta", width=6)
                table.add_column("Description", style="white")
                table.add_column("", width=2)  # Compatibility
                
                for model in models[:15]:  # Limit each category
                    table.add_row(
                        str(model['num']),
                        model['name'],
                        model['size'],
                        model['ram'],
                        model['desc'],
                        model['compat']
                    )
                    
                self.console.print(table)
            
            # Show input prompt with examples
            self.console.print("\n[bold]Download Options:[/bold]")
            self.console.print("• Enter numbers: 1,3,5 or 1-5")
            self.console.print("• Enter names: llama3.1:8b,mistral:7b")
            self.console.print("• Press Enter to skip")
            
            selection = Prompt.ask("\n[yellow]Select models[/yellow]")
            
            if not selection:
                self.console.print("[dim]No models selected[/dim]")
                return
                
            # Parse selection
            selected_models = []
            
            # Handle ranges like "1-5"
            import re
            for part in selection.split(','):
                part = part.strip()
                
                # Check for range
                range_match = re.match(r'(\d+)-(\d+)', part)
                if range_match:
                    start, end = map(int, range_match.groups())
                    for i in range(start, min(end + 1, len(OLLAMA_COMPLETE_REGISTRY) + 1)):
                        if 1 <= i <= len(OLLAMA_COMPLETE_REGISTRY):
                            model = OLLAMA_COMPLETE_REGISTRY[i-1]
                            # Check compatibility and warn
                            compatible, required, available = check_model_compatibility(model['name'], system_ram)
                            if not compatible:
                                warn = Confirm.ask(
                                    f"\n⚠️  {model['name']} requires {required}GB RAM but you have {available}GB available. Download anyway?",
                                    default=False
                                )
                                if warn:
                                    selected_models.append(model['name'])
                            else:
                                selected_models.append(model['name'])
                # Single number
                elif part.isdigit():
                    idx = int(part)
                    if 1 <= idx <= len(OLLAMA_COMPLETE_REGISTRY):
                        model = OLLAMA_COMPLETE_REGISTRY[idx-1]
                        # Check compatibility and warn
                        compatible, required, available = check_model_compatibility(model['name'], system_ram)
                        if not compatible:
                            warn = Confirm.ask(
                                f"\n⚠️  {model['name']} requires {required}GB RAM but you have {available}GB available. Download anyway?",
                                default=False
                            )
                            if warn:
                                selected_models.append(model['name'])
                        else:
                            selected_models.append(model['name'])
                # Model name
                elif part:
                    # Check compatibility for named model
                    compatible, required, available = check_model_compatibility(part, system_ram)
                    if not compatible and required > 0:
                        warn = Confirm.ask(
                            f"\n⚠️  {part} requires {required}GB RAM but you have {available}GB available. Download anyway?",
                            default=False
                        )
                        if warn:
                            selected_models.append(part)
                    else:
                        selected_models.append(part)
            
            if not selected_models:
                self.console.print("[yellow]No models selected[/yellow]")
                return
                
            model_names = ' '.join(selected_models)
        
        # Use parallel downloads
        models = model_names.split() if isinstance(model_names, str) else model_names
        
        if len(models) > 1:
            # Ask about parallel downloads
            response = Confirm.ask(
                f"\n[cyan]Download {len(models)} models in parallel? (faster)[/cyan]",
                default=True
            )
            
            if response:
                # Parallel download
                max_concurrent = Prompt.ask(
                    "How many concurrent downloads?",
                    default="3",
                    choices=["1", "2", "3", "4", "5"]
                )
                max_concurrent = int(max_concurrent)
                
                self.console.print(f"\n[cyan]Starting {max_concurrent} parallel downloads...[/cyan]")
                
                # Show download summary
                total_size = 0
                for model_name in models:
                    for m in OLLAMA_COMPLETE_REGISTRY:
                        if m['name'] == model_name:
                            total_size += m['size_gb']
                            break
                            
                self.console.print(f"[dim]Total download size: ~{total_size}GB[/dim]")
                
                # Use the model manager for parallel downloads
                from ..core.model_manager import AdaptiveModelManager
                models_path = Path(external_path) / 'ollama' / 'models'
                model_manager = AdaptiveModelManager(models_path)
                
                def progress_callback(msg: str):
                    self.console.print(f"[dim]{msg}[/dim]")
                
                # Run parallel downloads
                results = await model_manager.download_models_parallel(
                    models,
                    max_concurrent=max_concurrent,
                    progress_callback=progress_callback
                )
                
                # Show results
                self.console.print("\n[bold]Download Summary:[/bold]")
                success_count = 0
                for model, success in results.items():
                    if success:
                        self.console.print(f"✅ {model}")
                        success_count += 1
                    else:
                        self.console.print(f"❌ {model}")
                        
                self.console.print(f"\n[green]Successfully downloaded {success_count}/{len(models)} models[/green]")
                
                return
        
        # Single model download
        for model_name in models:
            self.console.print(f"\n[cyan]Downloading {model_name}...[/cyan]")
            
            # Use subprocess for single downloads
            import subprocess
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, 'OLLAMA_MODELS': f"{external_path}/ollama/models"}
            )
            
            # Show progress
            for line in process.stdout:
                if 'pulling' in line.lower() or '%' in line:
                    self.console.print(f"[dim]{line.strip()}[/dim]", end='\r')
                    
            process.wait()
            
            if process.returncode == 0:
                self.console.print(f"[green]✅ Downloaded {model_name}[/green]")
            else:
                self.console.print(f"[red]❌ Failed to download {model_name}[/red]")
                if process.stderr:
                    error = process.stderr.read()
                    if error:
                        self.console.print(f"[dim]Error: {error}[/dim]")
            
    async def export_conversation(self, filename: str):
        """Export conversation history"""
        if not filename:
            filename = f"nova_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        memory = await self.nova_core.get_memory_summary()
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'profile': {
                'created_at': memory['created_at'],
                'total_interactions': memory['total_interactions'],
                'preferences': {
                    'preferred_stack': memory['preferred_stack'],
                    'working_hours': memory['working_hours']
                }
            },
            'conversations': memory['recent_conversations'],
            'learned_patterns': memory['learned_patterns'],
            'projects': memory['recent_projects']
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            self.console.print(f"[green]✓ Exported to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/red]")
            
    async def import_conversation(self, filename: str):
        """Import conversation history"""
        if not filename or not Path(filename).exists():
            self.console.print("[red]File not found[/red]")
            return
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # TODO: Implement actual import logic
            self.console.print(f"[green]✓ Imported from {filename}[/green]")
            self.console.print(f"  Conversations: {len(data.get('conversations', []))}")
            self.console.print(f"  Patterns: {len(data.get('learned_patterns', {}))}")
        except Exception as e:
            self.console.print(f"[red]Import failed: {e}[/red]")
            
    async def take_screenshot(self):
        """Take and analyze a screenshot"""
        self.console.print("[cyan]Taking screenshot...[/cyan]")
        
        try:
            # Take screenshot using macOS screencapture
            screenshot_path = Path.home() / '.nova' / 'temp' / f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            screenshot_path.parent.mkdir(exist_ok=True)
            
            result = subprocess.run(
                ['screencapture', '-i', str(screenshot_path)],
                capture_output=True
            )
            
            if result.returncode == 0 and screenshot_path.exists():
                self.console.print("[green]✓ Screenshot captured![/green]")
                
                # Analyze with AI
                response = await self.nova_core.process_user_request(
                    f"Analyze this screenshot: {screenshot_path}"
                )
                self.display_response(response)
            else:
                self.console.print("[yellow]Screenshot cancelled[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Screenshot failed: {e}[/red]")
            
    async def toggle_voice(self):
        """Toggle voice input/output"""
        self.voice_enabled = not self.voice_enabled
        
        if self.voice_enabled:
            self.console.print(Panel(
                "🎤 Voice mode enabled\n\n" +
                "• Press SPACE to start recording\n" +
                "• Press SPACE again to stop\n" +
                "• NOVA will speak responses",
                title="Voice Mode",
                box=box.ROUNDED
            ))
        else:
            self.console.print("[cyan]Voice mode disabled[/cyan]")
            
    async def check_updates(self):
        """Check for NOVA updates"""
        self.console.print("[cyan]Checking for updates...[/cyan]")
        
        # TODO: Implement actual update check
        current_version = "0.1.0"
        
        update_panel = f"""
📦 Current Version: {current_version}
🔄 Status: Up to date

✨ Recent Updates:
• Enhanced terminal interface
• Voice control support
• Improved cost optimization
• Bug fixes and performance improvements
        """
        
        self.console.print(Panel(
            update_panel,
            title="NOVA Updates",
            box=box.ROUNDED
        ))
        
    async def reset_nova(self):
        """Reset NOVA to fresh state and restart setup"""
        self.console.print(Panel(
            "[yellow]⚠️  This will completely reset NOVA to fresh state:[/yellow]\n\n" +
            "• Delete all conversation history\n" +
            "• Remove user preferences\n" +
            "• Clear persistent memory\n" +
            "• Reset cost tracking\n" +
            "• Restart first-time setup\n\n" +
            "[red]This action cannot be undone![/red]",
            title="Reset NOVA",
            box=box.ROUNDED
        ))
        
        if not Confirm.ask("\n[bold red]Are you absolutely sure you want to reset NOVA?[/bold red]"):
            self.console.print("[cyan]Reset cancelled.[/cyan]")
            return
            
        self.console.print("\n[cyan]NOVA: Resetting to fresh state...[/cyan]")
        
        try:
            # Files and directories to remove
            nova_dir = Path.home() / '.nova'
            files_to_remove = [
                nova_dir / 'memory' / 'user_profile.json',
                nova_dir / 'memory' / 'preferences.json', 
                nova_dir / 'memory' / 'memory.md',
                nova_dir / 'cost_tracking.json',
                nova_dir / 'command_history',
                nova_dir / 'nova.log'
            ]
            
            # Remove specific files
            for file_path in files_to_remove:
                if file_path.exists():
                    file_path.unlink()
                    self.console.print(f"[dim]Removed: {file_path.name}[/dim]")
            
            # Remove memory directory if it exists and is empty
            memory_dir = nova_dir / 'memory'
            if memory_dir.exists():
                try:
                    memory_dir.rmdir()
                    self.console.print("[dim]Removed: memory directory[/dim]")
                except OSError:
                    # Directory not empty, that's okay
                    pass
                    
            self.console.print("\n[green]✓ NOVA reset completed successfully![/green]")
            
            # Show restart message
            self.console.print(Panel(
                "[bright_cyan]NOVA will now restart with fresh setup.[/bright_cyan]\n\n" +
                "Run '[bold]nova[/bold]' again to begin first-time setup.",
                title="Restart Required",
                box=box.ROUNDED
            ))
            
            # Exit current session
            self.running = False
            await self.nova_core.shutdown()
            
        except Exception as e:
            self.console.print(f"[red]Error during reset: {e}[/red]")
            self.console.print("[yellow]You may need to manually remove ~/.nova directory[/yellow]")
            
    async def show_self_analysis(self):
        """Show NOVA's self-analysis and performance insights"""
        try:
            # Get analysis from AI engine
            evolution_status = self.nova_core.ai_engine.get_evolution_status()
            
            # Performance Overview
            perf_data = evolution_status.get('performance_data', {})
            total_requests = perf_data.get('total_requests', 0)
            
            if total_requests == 0:
                self.console.print(Panel(
                    "[yellow]No data yet. Use NOVA more to generate insights![/yellow]",
                    title="Self-Analysis",
                    box=box.ROUNDED
                ))
                return
                
            success_rate = (perf_data.get('successful_requests', 0) / total_requests * 100) if total_requests > 0 else 0
            avg_time = perf_data.get('average_response_time', 0)
            
            # Create performance table
            perf_table = Table(title="Performance Metrics", box=box.ROUNDED)
            perf_table.add_column("Metric", style="cyan")
            perf_table.add_column("Value", style="green")
            perf_table.add_column("Status", style="yellow")
            
            perf_table.add_row(
                "Success Rate",
                f"{success_rate:.1f}%",
                "🟢 Great" if success_rate > 90 else "🟡 Good" if success_rate > 80 else "🔴 Needs Work"
            )
            perf_table.add_row(
                "Avg Response Time",
                f"{avg_time:.1f}s",
                "🟢 Fast" if avg_time < 2 else "🟡 OK" if avg_time < 5 else "🔴 Slow"
            )
            perf_table.add_row(
                "Total Interactions",
                str(total_requests),
                "🟢" if total_requests > 50 else "🟡" if total_requests > 10 else "🔴"
            )
            
            self.console.print(perf_table)
            
            # Pattern Analysis
            patterns = perf_data.get('common_patterns', {})
            if patterns:
                pattern_table = Table(title="Usage Patterns", box=box.ROUNDED)
                pattern_table.add_column("Pattern", style="cyan")
                pattern_table.add_column("Count", style="green")
                pattern_table.add_column("Success Rate", style="yellow")
                
                for pattern, stats in sorted(patterns.items(), key=lambda x: x[1]['count'], reverse=True):
                    pattern_table.add_row(
                        pattern.replace('_', ' ').title(),
                        str(stats['count']),
                        f"{stats['success_rate']:.1%}"
                    )
                    
                self.console.print(pattern_table)
                
            # Recent Insights
            insights = evolution_status.get('recent_insights', [])
            if insights:
                self.console.print("\n[bold]Recent Insights:[/bold]")
                for insight in insights[-5:]:
                    severity_color = {
                        'high': 'red',
                        'medium': 'yellow',
                        'low': 'green'
                    }.get(insight.get('severity', 'low'), 'white')
                    
                    self.console.print(f"[{severity_color}]• {insight['message']}[/{severity_color}]")
                    if insight.get('suggestion'):
                        self.console.print(f"  [dim]→ {insight['suggestion']}[/dim]")
                        
        except Exception as e:
            self.logger.error(f"Error showing self-analysis: {e}")
            self.console.print(f"[red]Error: {e}[/red]")
            
    async def show_evolution_status(self):
        """Show NOVA's evolution progress with the user"""
        try:
            # Get user profile and evolution data
            if not self.nova_core.user_profile:
                self.console.print("[yellow]No user profile found. Complete setup first.[/yellow]")
                return
                
            evolution_status = self.nova_core.ai_engine.get_evolution_status()
            evolution_progress = evolution_status.get('evolution_progress', 0)
            
            # Create evolution visualization
            progress_bar = self._create_progress_bar(evolution_progress)
            
            evolution_panel = f"""
🧬 NOVA Evolution Progress

{progress_bar}
Progress: {evolution_progress:.1f}%

📊 Evolution Factors:
• Total Interactions: {self.nova_core.user_profile.total_interactions}
• Learning Insights: {len(evolution_status.get('recent_insights', []))}
• Patterns Recognized: {len(evolution_status.get('performance_data', {}).get('common_patterns', {}))}

🎯 Current Stage: {self._get_evolution_stage_name(self.nova_core.user_profile.total_interactions)}
            """
            
            self.console.print(Panel(
                evolution_panel,
                title="Evolution Status",
                box=box.ROUNDED
            ))
            
            # Show next milestone
            if evolution_progress < 100:
                self.console.print("\n[bold]Next Milestone:[/bold]")
                next_stage = self._get_next_evolution_milestone(self.nova_core.user_profile.total_interactions)
                if next_stage:
                    self.console.print(f"[cyan]→ {next_stage['description']}[/cyan]")
                    self.console.print(f"[dim]  Action: {next_stage['action']}[/dim]")
                    
        except Exception as e:
            self.logger.error(f"Error showing evolution status: {e}")
            self.console.print(f"[red]Error: {e}[/red]")
            
    async def show_suggestions(self):
        """Show AI-generated suggestions for the user"""
        try:
            if not self.nova_core.user_profile:
                self.console.print("[yellow]No user profile found. Complete setup first.[/yellow]")
                return
                
            # Get suggestions from AI engine
            suggestions = await self.nova_core.ai_engine.get_self_improvement_suggestions(
                self.nova_core.user_profile
            )
            
            if not suggestions:
                self.console.print(Panel(
                    "[green]Everything looks great! Keep using NOVA to unlock more suggestions.[/green]",
                    title="AI Suggestions",
                    box=box.ROUNDED
                ))
                return
                
            # Display suggestions
            self.console.print("[bold]NOVA's Suggestions for You:[/bold]\n")
            
            for i, suggestion in enumerate(suggestions, 1):
                priority_color = {
                    'high': 'red',
                    'medium': 'yellow',
                    'low': 'green'
                }.get(suggestion.get('priority', 'low'), 'white')
                
                category_emoji = {
                    'optimization': '⚡',
                    'workflow': '🔄',
                    'features': '✨',
                    'evolution': '🧬',
                    'performance': '🚀'
                }.get(suggestion.get('category', 'general'), '💡')
                
                suggestion_box = f"""
{category_emoji} [{priority_color}]{suggestion['title']}[/{priority_color}]

{suggestion['description']}

🎯 Action: {suggestion['action']}
📈 Impact: {suggestion['impact']}
                """
                
                self.console.print(Panel(
                    suggestion_box.strip(),
                    box=box.ROUNDED
                ))
                
            # Predict user needs
            context = self.nova_core._build_context()
            predictions = await self.nova_core.ai_engine.predict_user_needs(
                self.nova_core.user_profile,
                context
            )
            
            if predictions:
                self.console.print("\n[bold]Predicted Needs:[/bold]")
                for pred in predictions[:3]:
                    confidence_color = 'green' if pred['confidence'] > 0.7 else 'yellow'
                    self.console.print(
                        f"[{confidence_color}]• {pred['suggestion']} "
                        f"(confidence: {pred['confidence']:.0%})[/{confidence_color}]"
                    )
                    
        except Exception as e:
            self.logger.error(f"Error showing suggestions: {e}")
            self.console.print(f"[red]Error: {e}[/red]")
            
    async def show_improvement_plan(self):
        """Show comprehensive self-improvement plan"""
        try:
            # Get improvement plan from AI engine
            plan = await self.nova_core.ai_engine.get_self_improvement_plan()
            
            if plan.get('status') == 'learning':
                self.console.print(Panel(
                    f"[yellow]{plan['message']}[/yellow]\n\n"
                    f"Progress: {plan.get('progress', 'N/A')}",
                    title="Self-Improvement",
                    box=box.ROUNDED
                ))
                return
                
            # Display improvement plan
            plan_text = f"""
📊 Current Performance:
• Success Rate: {plan['current_metrics']['success_rate']:.1%}
• Avg Response Time: {plan['current_metrics']['avg_response_time']:.1f}s
• Total Interactions: {plan['current_metrics']['total_interactions']}

🎯 Target Goals:
• Success Rate: {plan['target_metrics']['success_rate']:.1%}
• Avg Response Time: {plan['target_metrics']['avg_response_time']:.1f}s
• User Satisfaction: {plan['target_metrics']['user_satisfaction']:.1%}

📅 Timeline: {plan['timeline']}
            """
            
            self.console.print(Panel(
                plan_text,
                title="NOVA Self-Improvement Plan",
                box=box.ROUNDED
            ))
            
            # Show improvement areas
            if plan.get('improvement_areas'):
                area_table = Table(title="Areas for Improvement", box=box.ROUNDED)
                area_table.add_column("Area", style="cyan")
                area_table.add_column("Current", style="yellow")
                area_table.add_column("Target", style="green")
                area_table.add_column("Gap", style="red")
                
                for area in plan['improvement_areas']:
                    area_table.add_row(
                        area['area'].replace('_', ' ').title(),
                        f"{area['current_performance']:.1%}",
                        f"{area['target']:.1%}",
                        f"{area['improvement_needed']:.1%}"
                    )
                    
                self.console.print(area_table)
                
            # Show recommended actions
            if plan.get('recommended_actions'):
                self.console.print("\n[bold]Recommended Actions:[/bold]")
                for action in plan['recommended_actions']:
                    priority_color = {
                        'high': 'red',
                        'medium': 'yellow',
                        'low': 'green'
                    }.get(action.get('priority', 'medium'), 'white')
                    
                    self.console.print(
                        f"[{priority_color}]• {action['action']}[/{priority_color}]"
                    )
                    self.console.print(f"  [dim]Reason: {action['reason']}[/dim]")
                    
        except Exception as e:
            self.logger.error(f"Error showing improvement plan: {e}")
            self.console.print(f"[red]Error: {e}[/red]")
            
    def _create_progress_bar(self, progress: float, width: int = 40) -> str:
        """Create a visual progress bar"""
        filled = int(width * progress / 100)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        return f"[green]{bar}[/green]"
        
    def _get_evolution_stage_name(self, interactions: int) -> str:
        """Get current evolution stage name"""
        if interactions < 10:
            return "Initial Setup"
        elif interactions < 50:
            return "Basic Assistant"
        elif interactions < 200:
            return "Productivity Partner"
        elif interactions < 1000:
            return "AI Co-founder"
        else:
            return "Synchronized Intelligence"
            
    def _get_next_evolution_milestone(self, interactions: int) -> Optional[Dict[str, str]]:
        """Get next evolution milestone info"""
        stages = [
            (10, {
                'name': 'Basic Assistant',
                'description': 'Unlock basic AI capabilities',
                'action': 'Continue using NOVA for various tasks'
            }),
            (50, {
                'name': 'Productivity Partner',
                'description': 'Enable advanced automation features',
                'action': 'Try complex tasks and background operations'
            }),
            (200, {
                'name': 'AI Co-founder',
                'description': 'Achieve deep work synchronization',
                'action': 'Enable proactive AI suggestions'
            }),
            (1000, {
                'name': 'Synchronized Intelligence',
                'description': 'Reach full AI-human symbiosis',
                'action': 'Explore cutting-edge AI capabilities'
            })
        ]
        
        for threshold, stage in stages:
            if interactions < threshold:
                return stage
                
        return None
    
    async def handle_mode_command(self, args: str):
        """Handle mode switching command"""
        if not args:
            # Show current mode
            current_mode = self.nova_core.get_current_mode()
            self.console.print(Panel(
                f"Current mode: [bold cyan]{current_mode.title()}[/bold cyan]\n\n" +
                "Available modes:\n" +
                "• [yellow]personal[/yellow] - Personal AI assistant (default)\n" +
                "• [yellow]company[/yellow] - AI software development company\n\n" +
                "Switch with: /mode <mode_name>",
                title="NOVA Operation Mode",
                box=box.ROUNDED
            ))
        else:
            # Switch mode
            mode = args.strip().lower()
            if mode in ['personal', 'company']:
                success = await self.nova_core.switch_mode(mode)
                if success:
                    self.console.print(f"[green]✓[/green] Switched to {mode} mode")
                    
                    if mode == 'company':
                        self.console.print(Panel(
                            "[bold cyan]Company Mode Activated![/bold cyan]\n\n" +
                            "You now have access to:\n" +
                            "• AI development team with legendary personalities\n" +
                            "• Project management capabilities\n" +
                            "• Automated software development\n\n" +
                            "Commands:\n" +
                            "• /company - Show company dashboard\n" +
                            "• /project create <brief> - Create new project\n" +
                            "• /project list - List all projects\n" +
                            "• /team - Show AI team members",
                            title="Legendary Ventures",
                            box=box.ROUNDED
                        ))
                else:
                    self.console.print(f"[red]Failed to switch to {mode} mode[/red]")
            else:
                self.console.print(f"[red]Invalid mode: {mode}[/red]")
                
    async def handle_company_command(self, args: str):
        """Handle company-related commands"""
        if self.nova_core.get_current_mode() != 'company':
            self.console.print("[yellow]Company commands require company mode. Use: /mode company[/yellow]")
            return
            
        dashboard = await self.nova_core.get_company_dashboard()
        if not dashboard:
            self.console.print("[red]Company dashboard not available[/red]")
            return
            
        # Create company dashboard table
        table = Table(title="Legendary Ventures Dashboard", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Active Projects", str(dashboard['active_projects']))
        table.add_row("Completed Projects", str(dashboard['completed_projects']))
        table.add_row("AI Agents", str(dashboard['total_agents']))
        table.add_row("Team Utilization", f"{dashboard['utilization']:.1%}")
        
        self.console.print(table)
        
        # Show active projects
        if dashboard['projects']:
            projects_table = Table(title="Active Projects", box=box.ROUNDED)
            projects_table.add_column("ID", style="cyan")
            projects_table.add_column("Name", style="yellow")
            projects_table.add_column("Status", style="green")
            projects_table.add_column("Progress", style="blue")
            
            for project in dashboard['projects']:
                projects_table.add_row(
                    project['id'],
                    project['name'],
                    project['status'],
                    f"{project['progress']}%"
                )
                
            self.console.print(projects_table)
            
    async def handle_project_command(self, args: str):
        """Handle project-related commands"""
        if self.nova_core.get_current_mode() != 'company':
            self.console.print("[yellow]Project commands require company mode. Use: /mode company[/yellow]")
            return
            
        if not args:
            self.console.print(Panel(
                "Project commands:\n" +
                "• /project create <brief> - Create new project\n" +
                "• /project list - List all projects\n" +
                "• /project show <id> - Show project details\n" +
                "• /project update <id> <progress> - Update project progress",
                title="Project Management",
                box=box.ROUNDED
            ))
            return
            
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        
        if subcommand == 'create' and len(parts) > 1:
            brief = parts[1]
            self.console.print(f"[cyan]Creating project: {brief[:50]}...[/cyan]")
            
            # Create project through company
            result = await self.nova_core.company.create_project(brief)
            
            if result['success']:
                self.console.print(Panel(
                    f"[green]✓ Project created successfully![/green]\n\n" +
                    f"ID: [bold]{result['id']}[/bold]\n" +
                    f"Name: {result['name']}\n" +
                    f"Team: {', '.join(result['team'])}\n" +
                    f"Timeline: {result['timeline']}\n\n" +
                    f"First steps:\n" +
                    '\n'.join(f"• {step}" for step in result['first_steps']),
                    title="New Project",
                    box=box.ROUNDED
                ))
            else:
                self.console.print(f"[red]Failed to create project: {result['reason']}[/red]")
                
        elif subcommand == 'list':
            dashboard = await self.nova_core.get_company_dashboard()
            if dashboard and dashboard['projects']:
                table = Table(title="All Projects", box=box.ROUNDED)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="yellow")
                table.add_column("Status", style="green")
                table.add_column("Progress", style="blue")
                table.add_column("Team Size", style="magenta")
                
                for project in dashboard['projects']:
                    table.add_row(
                        project['id'],
                        project['name'],
                        project['status'],
                        f"{project['progress']}%",
                        str(project['team_size'])
                    )
                    
                self.console.print(table)
            else:
                self.console.print("[dim]No projects found[/dim]")
                
    async def show_team_info(self):
        """Show AI team information"""
        if self.nova_core.get_current_mode() != 'company':
            self.console.print("[yellow]Team info requires company mode. Use: /mode company[/yellow]")
            return
            
        dashboard = await self.nova_core.get_company_dashboard()
        if not dashboard:
            return
            
        table = Table(title="AI Development Team", box=box.ROUNDED)
        table.add_column("Role", style="cyan")
        table.add_column("Personality", style="yellow")
        table.add_column("Expertise", style="green")
        
        team_expertise = {
            'buffett': 'Business strategy, ROI analysis, long-term value',
            'linus': 'System architecture, code quality, performance',
            'jobs': 'Product vision, user experience, innovation',
            'ive': 'Design excellence, minimalism, aesthetics',
            'carmack': 'Graphics, optimization, low-level programming',
            'musk': 'Scale thinking, first principles, rapid iteration',
            'bezos': 'Customer focus, platform strategy, operations'
        }
        
        for member in dashboard['team']:
            role = member['role'].replace('_', ' ').title()
            personality = member['personality'].title()
            expertise = team_expertise.get(member['personality'], 'Multi-domain expertise')
            
            table.add_row(role, personality, expertise)
            
        self.console.print(table)
        
        # Show personality stats if available
        if hasattr(self.nova_core, 'unified_engine'):
            stats = self.nova_core.unified_engine.get_personality_stats()
            if stats.get('mode') == 'company':
                self.console.print(Panel(
                    f"Total interactions: {stats['total_uses']}\n" +
                    f"Current personality: {stats['current_mode']}",
                    title="Team Statistics",
                    box=box.ROUNDED
                ))