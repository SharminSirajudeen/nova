"""
Project Manager for NOVA Company Mode
Manages AI development projects
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid


class ProjectStatus(Enum):
    """Project status states"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


@dataclass
class Project:
    """Represents an AI development project"""
    id: str
    name: str
    client: str
    description: str
    requirements: List[str]
    budget: float
    timeline_weeks: int
    tech_stack: List[str]
    team: List[str]
    status: ProjectStatus = ProjectStatus.PLANNING
    progress: float = 0.0
    current_phase: str = "Initiation"
    roadmap: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_progress(self, progress: float):
        """Update project progress"""
        self.progress = min(100.0, max(0.0, progress))
        self.updated_at = datetime.now()
        
    def add_team_member(self, member: str):
        """Add a team member"""
        if member not in self.team:
            self.team.append(member)
            self.updated_at = datetime.now()
            
    def update_status(self, status: ProjectStatus):
        """Update project status"""
        self.status = status
        self.updated_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'client': self.client,
            'description': self.description,
            'requirements': self.requirements,
            'budget': self.budget,
            'timeline_weeks': self.timeline_weeks,
            'tech_stack': self.tech_stack,
            'team': self.team,
            'status': self.status.value,
            'progress': self.progress,
            'current_phase': self.current_phase,
            'roadmap': self.roadmap,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ProjectManager:
    """Manages all AI development projects"""
    
    def __init__(self):
        self.projects: Dict[str, Project] = {}
        
    def add_project(self, project: Project) -> str:
        """Add a new project"""
        self.projects[project.id] = project
        return project.id
        
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        return self.projects.get(project_id)
        
    def get_active_projects(self) -> List[Project]:
        """Get all active projects"""
        return [
            p for p in self.projects.values()
            if p.status in [ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS, ProjectStatus.REVIEW]
        ]
        
    def get_completed_projects(self) -> List[Project]:
        """Get all completed projects"""
        return [p for p in self.projects.values() if p.status == ProjectStatus.COMPLETED]
        
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update a project"""
        project = self.get_project(project_id)
        if not project:
            return False
            
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
                
        project.updated_at = datetime.now()
        return True
        
    def generate_project_report(self, project_id: str) -> Dict[str, Any]:
        """Generate a detailed project report"""
        project = self.get_project(project_id)
        if not project:
            return {}
            
        active_days = (datetime.now() - project.created_at).days
        
        return {
            'project': project.to_dict(),
            'metrics': {
                'days_active': active_days,
                'team_size': len(project.team),
                'requirements_count': len(project.requirements),
                'estimated_completion': f"{int((100 - project.progress) / 10)} weeks",
                'budget_per_week': project.budget / project.timeline_weeks if project.timeline_weeks > 0 else 0
            },
            'health': self._assess_project_health(project)
        }
        
    def _assess_project_health(self, project: Project) -> str:
        """Assess project health"""
        # Simple health assessment
        if project.progress >= 80:
            return "Excellent - nearing completion"
        elif project.progress >= 50:
            return "Good - on track"
        elif project.progress >= 20:
            return "Fair - needs attention"
        else:
            return "At Risk - requires immediate review"