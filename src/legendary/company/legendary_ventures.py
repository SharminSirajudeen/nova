"""
Legendary Ventures - AI Software Development Company
Simplified version for NOVA integration
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

from .project_manager import ProjectManager, Project, ProjectStatus
from ..personalities.personality_engine import PersonalityEngine
from ..personalities.legendary_personalities import LegendaryPersonality
from ...models import Task, TaskComplexity
from ...utils.ollama_client import OllamaClient


@dataclass
class CompanyMetrics:
    """Company performance metrics"""
    projects_completed: int = 0
    active_projects: int = 0
    total_revenue: float = 0.0
    client_satisfaction: float = 0.0
    team_utilization: float = 0.0
    average_project_time: float = 0.0


class LegendaryVentures:
    """
    AI-powered software development company
    Simplified for NOVA integration
    """
    
    def __init__(self, company_name: str = "Legendary Ventures"):
        self.logger = logging.getLogger('NOVA.LegendaryVentures')
        self.company_name = company_name
        self.company_path = Path.home() / '.nova' / 'company'
        
        # Core components
        self.project_manager = ProjectManager()
        self.personality_engine = PersonalityEngine()
        self.ollama = OllamaClient()
        
        # Virtual team (personality-based agents)
        self.team = {
            'ceo': LegendaryPersonality.BUFFETT,
            'cto': LegendaryPersonality.LINUS,
            'cpo': LegendaryPersonality.JOBS,
            'lead_designer': LegendaryPersonality.IVE,
            'lead_engineer': LegendaryPersonality.CARMACK,
            'innovator': LegendaryPersonality.MUSK,
            'strategist': LegendaryPersonality.BEZOS
        }
        
        # Metrics
        self.metrics = CompanyMetrics()
        
        # Setup directories
        self._setup_directories()
        
    def _setup_directories(self):
        """Create company directory structure"""
        directories = [
            "projects", "clients", "deliverables", "documentation",
            "metrics", "templates", "research"
        ]
        
        for dir_name in directories:
            (self.company_path / dir_name).mkdir(parents=True, exist_ok=True)
            
    async def initialize(self):
        """Initialize company systems"""
        self.logger.info("Initializing Legendary Ventures...")
        
        # Load any existing projects
        # TODO: Implement project persistence
        
        return True
        
    async def create_project(self, 
                           brief: str,
                           budget: Optional[float] = None,
                           timeline_weeks: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new project from client brief
        """
        self.logger.info(f"Creating new project from brief: {brief[:50]}...")
        
        # Phase 1: Executive analysis using personalities
        analysis = await self._analyze_project_request(brief, budget, timeline_weeks)
        
        if not analysis['feasible']:
            return {
                'success': False,
                'reason': analysis['reason'],
                'recommendations': analysis.get('recommendations', [])
            }
            
        # Phase 2: Create project
        project = Project(
            id=str(uuid.uuid4())[:8],
            name=analysis['project_name'],
            client="Direct Client",  # Simplified for NOVA
            description=brief,
            requirements=analysis['requirements'],
            budget=budget or analysis['estimated_budget'],
            timeline_weeks=timeline_weeks or analysis['estimated_timeline'],
            tech_stack=analysis['tech_stack'],
            team=analysis['recommended_team']
        )
        
        # Phase 3: Create initial roadmap
        roadmap = await self._create_roadmap(project)
        project.roadmap = roadmap
        
        # Register project
        self.project_manager.add_project(project)
        
        # Update metrics
        self.metrics.active_projects += 1
        self.metrics.team_utilization = self._calculate_utilization()
        
        return {
            'success': True,
            'id': project.id,
            'name': project.name,
            'team': project.team,
            'tech_stack': project.tech_stack,
            'timeline': f"{project.timeline_weeks} weeks",
            'first_steps': roadmap.get('first_steps', []),
            'message': f"Project '{project.name}' created successfully!"
        }
        
    async def _analyze_project_request(self, brief: str, budget: Optional[float], 
                                     timeline: Optional[int]) -> Dict[str, Any]:
        """Analyze project using executive team personalities"""
        
        # CEO (Buffett) analyzes business viability
        ceo_task = Task(
            content=f"As Warren Buffett, analyze this business opportunity: {brief}. Consider ROI, sustainability, and long-term value.",
            complexity=TaskComplexity.COMPLEX,
            context={'role': 'CEO', 'focus': 'business_viability'}
        )
        
        ceo_prompt = self.personality_engine.build_prompt(
            task=ceo_task,
            personality=LegendaryPersonality.BUFFETT,
            context={}
        )
        
        ceo_analysis = await self.ollama.generate(
            model="llama3.2:3b",  # Use a smaller model for efficiency
            prompt=ceo_prompt,
            temperature=0.7
        )
        
        # CTO (Linus) assesses technical feasibility
        cto_task = Task(
            content=f"As Linus Torvalds, assess technical feasibility: {brief}. Focus on architecture, scalability, and implementation challenges.",
            complexity=TaskComplexity.COMPLEX,
            context={'role': 'CTO', 'focus': 'technical_feasibility'}
        )
        
        cto_prompt = self.personality_engine.build_prompt(
            task=cto_task,
            personality=LegendaryPersonality.LINUS,
            context={}
        )
        
        cto_analysis = await self.ollama.generate(
            model="llama3.2:3b",
            prompt=cto_prompt,
            temperature=0.6
        )
        
        # Extract key information (simplified parsing)
        feasible = "not feasible" not in ceo_analysis.lower() and "impossible" not in cto_analysis.lower()
        
        # Generate project details
        project_name = self._extract_project_name(brief)
        requirements = self._extract_requirements(brief, ceo_analysis, cto_analysis)
        tech_stack = self._extract_tech_stack(cto_analysis, brief)
        
        return {
            'feasible': feasible,
            'project_name': project_name,
            'requirements': requirements,
            'tech_stack': tech_stack,
            'estimated_budget': budget or 50000,  # Default budget
            'estimated_timeline': timeline or 12,  # Default 12 weeks
            'recommended_team': self._select_team(tech_stack, requirements),
            'reason': "Project analysis complete" if feasible else "Project not feasible at this time",
            'ceo_insights': ceo_analysis[:200],
            'cto_insights': cto_analysis[:200]
        }
        
    def _extract_project_name(self, brief: str) -> str:
        """Extract or generate project name"""
        # Simple extraction - look for quoted names or generate from brief
        if '"' in brief:
            start = brief.find('"') + 1
            end = brief.find('"', start)
            if end > start:
                return brief[start:end]
                
        # Generate from first few words
        words = brief.split()[:5]
        return " ".join(words).title() + " Project"
        
    def _extract_requirements(self, brief: str, ceo_analysis: str, cto_analysis: str) -> List[str]:
        """Extract project requirements"""
        requirements = []
        
        # Common requirement keywords
        keywords = ['must', 'should', 'need', 'require', 'feature', 'functionality']
        
        for line in brief.split('.'):
            if any(keyword in line.lower() for keyword in keywords):
                requirements.append(line.strip())
                
        # Add some standard requirements
        if 'web' in brief.lower() or 'app' in brief.lower():
            requirements.extend([
                "Responsive user interface",
                "Secure authentication",
                "Database integration",
                "API development"
            ])
            
        return requirements[:10]  # Limit to 10 requirements
        
    def _extract_tech_stack(self, cto_analysis: str, brief: str) -> List[str]:
        """Extract recommended tech stack"""
        tech_stack = []
        
        # Common technology patterns
        tech_patterns = {
            'python': ['flask', 'django', 'fastapi'],
            'javascript': ['react', 'node.js', 'express'],
            'mobile': ['react native', 'flutter', 'swift'],
            'database': ['postgresql', 'mongodb', 'redis'],
            'cloud': ['aws', 'gcp', 'docker']
        }
        
        brief_lower = (brief + " " + cto_analysis).lower()
        
        for category, techs in tech_patterns.items():
            if category in brief_lower:
                tech_stack.extend([t for t in techs if t in brief_lower][:2])
                
        # Default stack if nothing specific found
        if not tech_stack:
            if 'web' in brief_lower:
                tech_stack = ['react', 'node.js', 'postgresql']
            else:
                tech_stack = ['python', 'fastapi', 'postgresql']
                
        return tech_stack
        
    def _select_team(self, tech_stack: List[str], requirements: List[str]) -> List[str]:
        """Select team members based on project needs"""
        team = ['Project Manager', 'Tech Lead']
        
        # Add specialists based on tech stack
        if any(web in str(tech_stack) for web in ['react', 'vue', 'angular']):
            team.append('Frontend Developer')
            
        if any(backend in str(tech_stack) for backend in ['node', 'python', 'java']):
            team.append('Backend Developer')
            
        if any(ml in str(requirements) for ml in ['ai', 'machine learning', 'ml']):
            team.append('AI/ML Engineer')
            
        if len(requirements) > 5:
            team.append('QA Engineer')
            
        team.append('DevOps Engineer')
        
        return team
        
    async def _create_roadmap(self, project: Project) -> Dict[str, Any]:
        """Create project roadmap using Jobs's product thinking"""
        task = Task(
            content=f"Create a development roadmap for: {project.description}. Tech stack: {project.tech_stack}",
            complexity=TaskComplexity.COMPLEX,
            context={'project': project.to_dict()}
        )
        
        prompt = self.personality_engine.build_prompt(
            task=task,
            personality=LegendaryPersonality.JOBS,
            context={}
        )
        
        roadmap_response = await self.ollama.generate(
            model="llama3.2:3b",
            prompt=prompt,
            temperature=0.7
        )
        
        # Extract phases (simplified)
        return {
            'phases': [
                'Discovery & Planning',
                'Design & Architecture', 
                'Core Development',
                'Testing & Refinement',
                'Launch & Iteration'
            ],
            'first_steps': [
                'Set up development environment',
                'Create project repository',
                'Design system architecture',
                'Build initial prototype',
                'Gather user feedback'
            ],
            'milestones': [
                {'week': 2, 'deliverable': 'Technical specification'},
                {'week': 4, 'deliverable': 'UI/UX designs'},
                {'week': 8, 'deliverable': 'MVP release'},
                {'week': 12, 'deliverable': 'Production release'}
            ]
        }
        
    def _calculate_utilization(self) -> float:
        """Calculate team utilization"""
        active_projects = len(self.project_manager.get_active_projects())
        total_capacity = len(self.team) * 2  # Each personality can handle 2 projects
        
        return min(1.0, active_projects / total_capacity) if total_capacity > 0 else 0.0
        
    async def get_dashboard(self) -> Dict[str, Any]:
        """Get company dashboard"""
        active_projects = self.project_manager.get_active_projects()
        completed_projects = self.project_manager.get_completed_projects()
        
        return {
            'company': self.company_name,
            'active_projects': len(active_projects),
            'completed_projects': len(completed_projects),
            'total_agents': len(self.team),
            'available_models': 10,  # Simplified
            'utilization': self.metrics.team_utilization,
            'team': [
                {'role': role, 'personality': personality.value}
                for role, personality in self.team.items()
            ],
            'projects': [
                {
                    'id': p.id,
                    'name': p.name,
                    'status': p.status.value,
                    'progress': p.progress,
                    'team_size': len(p.team)
                }
                for p in active_projects
            ],
            'metrics': asdict(self.metrics)
        }
        
    async def update_project_progress(self, project_id: str, progress: float) -> bool:
        """Update project progress"""
        project = self.project_manager.get_project(project_id)
        if project:
            project.update_progress(progress)
            
            # Update status based on progress
            if progress >= 100:
                project.update_status(ProjectStatus.COMPLETED)
                self.metrics.projects_completed += 1
                self.metrics.active_projects -= 1
            elif progress >= 80:
                project.update_status(ProjectStatus.REVIEW)
            elif progress > 0:
                project.update_status(ProjectStatus.IN_PROGRESS)
                
            return True
        return False
        
    async def get_project_details(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed project information"""
        return self.project_manager.generate_project_report(project_id)