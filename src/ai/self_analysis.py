"""
NOVA Self-Analysis and Evolution Engine
Enables NOVA to analyze its own performance and suggest improvements
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import asyncio

from ..models import (
    TaskComplexity,
    Model,
    ModelType,
    UserProfile
)


class SelfAnalysisEngine:
    """
    Analyzes NOVA's performance and suggests improvements
    Tracks patterns, learns from interactions, and evolves
    """
    
    def __init__(self, memory_path: Path = None):
        self.logger = logging.getLogger('NOVA.SelfAnalysis')
        self.memory_path = memory_path or Path.home() / '.nova' / 'analytics'
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_data = self._load_performance_data()
        self.suggestions_made = []
        self.learning_insights = []
        
    def _load_performance_data(self) -> Dict[str, Any]:
        """Load historical performance data"""
        perf_file = self.memory_path / 'performance.json'
        
        if perf_file.exists():
            with open(perf_file, 'r') as f:
                return json.load(f)
                
        return {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'model_performance': {},
            'task_complexity_stats': {},
            'user_satisfaction': {},
            'common_patterns': {},
            'improvement_areas': [],
            'evolution_timeline': []
        }
        
    def save_performance_data(self):
        """Save performance data to disk"""
        perf_file = self.memory_path / 'performance.json'
        
        with open(perf_file, 'w') as f:
            json.dump(self.performance_data, f, indent=2, default=str)
            
    async def analyze_interaction(self, request: str, response: str, 
                                 model_used: str, processing_time: float,
                                 success: bool, user_feedback: Optional[str] = None):
        """Analyze a single interaction and update learning"""
        # Update basic stats
        self.performance_data['total_requests'] += 1
        
        if success:
            self.performance_data['successful_requests'] += 1
        else:
            self.performance_data['failed_requests'] += 1
            
        # Update average response time
        total = self.performance_data['total_requests']
        avg = self.performance_data['average_response_time']
        self.performance_data['average_response_time'] = (
            (avg * (total - 1) + processing_time) / total
        )
        
        # Track model performance
        if model_used not in self.performance_data['model_performance']:
            self.performance_data['model_performance'][model_used] = {
                'uses': 0,
                'successes': 0,
                'avg_time': 0.0,
                'satisfaction_score': 0.0
            }
            
        model_stats = self.performance_data['model_performance'][model_used]
        model_stats['uses'] += 1
        if success:
            model_stats['successes'] += 1
            
        # Detect patterns
        await self._detect_patterns(request, response, success)
        
        # Generate insights
        insights = await self._generate_insights()
        if insights:
            self.learning_insights.extend(insights)
            
        self.save_performance_data()
        
    async def _detect_patterns(self, request: str, response: str, success: bool):
        """Detect patterns in user interactions"""
        # Extract key phrases
        words = request.lower().split()
        
        # Track common request types
        if 'code' in words or 'implement' in words:
            self._track_pattern('code_generation', success)
        elif 'explain' in words or 'what' in words:
            self._track_pattern('explanation', success)
        elif 'fix' in words or 'debug' in words:
            self._track_pattern('debugging', success)
        elif 'analyze' in words or 'review' in words:
            self._track_pattern('analysis', success)
            
    def _track_pattern(self, pattern_type: str, success: bool):
        """Track pattern occurrence"""
        if pattern_type not in self.performance_data['common_patterns']:
            self.performance_data['common_patterns'][pattern_type] = {
                'count': 0,
                'success_rate': 0.0
            }
            
        pattern = self.performance_data['common_patterns'][pattern_type]
        pattern['count'] += 1
        
        # Update success rate
        if success:
            current_rate = pattern['success_rate']
            pattern['success_rate'] = (
                (current_rate * (pattern['count'] - 1) + 1) / pattern['count']
            )
        else:
            current_rate = pattern['success_rate']
            pattern['success_rate'] = (
                (current_rate * (pattern['count'] - 1)) / pattern['count']
            )
            
    async def _generate_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from performance data"""
        insights = []
        
        # Check success rate
        total = self.performance_data['total_requests']
        if total > 10:  # Need enough data
            success_rate = self.performance_data['successful_requests'] / total
            
            if success_rate < 0.8:
                insights.append({
                    'type': 'performance',
                    'severity': 'high',
                    'message': f"Success rate is {success_rate:.1%}. Consider improving error handling.",
                    'suggestion': "Add more robust fallback mechanisms"
                })
                
        # Check response times
        avg_time = self.performance_data['average_response_time']
        if avg_time > 5.0:
            insights.append({
                'type': 'performance',
                'severity': 'medium',
                'message': f"Average response time is {avg_time:.1f}s. Consider optimization.",
                'suggestion': "Use more local models or optimize prompts"
            })
            
        # Check model performance
        for model, stats in self.performance_data['model_performance'].items():
            if stats['uses'] > 5:
                success_rate = stats['successes'] / stats['uses']
                if success_rate < 0.7:
                    insights.append({
                        'type': 'model',
                        'severity': 'medium',
                        'message': f"Model {model} has low success rate: {success_rate:.1%}",
                        'suggestion': f"Consider replacing {model} with a better alternative"
                    })
                    
        return insights
        
    async def suggest_improvements(self, user_profile: UserProfile) -> List[Dict[str, Any]]:
        """Suggest improvements based on analysis"""
        suggestions = []
        
        # Analyze user patterns
        if user_profile.total_interactions > 20:
            # Check most common request types
            patterns = self.performance_data['common_patterns']
            
            # Suggest specialized models
            if patterns.get('code_generation', {}).get('count', 0) > 10:
                suggestions.append({
                    'category': 'optimization',
                    'priority': 'high',
                    'title': 'Code Generation Optimization',
                    'description': 'You frequently generate code. Consider downloading specialized code models.',
                    'action': 'Download codellama:7b or codellama:13b for better code generation',
                    'impact': 'Improve code quality and reduce generation time by 40%'
                })
                
            if patterns.get('debugging', {}).get('count', 0) > 5:
                suggestions.append({
                    'category': 'workflow',
                    'priority': 'medium',
                    'title': 'Debugging Workflow Enhancement',
                    'description': 'You often debug code. NOVA can be more proactive.',
                    'action': 'Enable automatic error detection mode',
                    'impact': 'Catch errors before they occur'
                })
                
        # Check resource usage
        if self.performance_data['average_response_time'] > 3.0:
            suggestions.append({
                'category': 'performance',
                'priority': 'high',
                'title': 'Response Time Optimization',
                'description': 'NOVA is taking longer to respond than optimal.',
                'action': 'Enable response caching and download faster local models',
                'impact': 'Reduce response time by up to 60%'
            })
            
        # Check for unused capabilities
        if user_profile.total_interactions > 10:
            used_features = set()
            for pattern in patterns.keys():
                used_features.add(pattern)
                
            unused_features = {'voice_control', 'automation', 'background_tasks'} - used_features
            
            if unused_features:
                suggestions.append({
                    'category': 'features',
                    'priority': 'low',
                    'title': 'Discover New Capabilities',
                    'description': f'You haven\'t used: {", ".join(unused_features)}',
                    'action': 'Try voice commands or automation features',
                    'impact': 'Increase productivity by 30%'
                })
                
        # Evolution suggestions
        evolution_stage = self._determine_evolution_stage(user_profile)
        if evolution_stage['next_milestone']:
            suggestions.append({
                'category': 'evolution',
                'priority': 'medium',
                'title': f'Evolve to {evolution_stage["next_milestone"]}',
                'description': evolution_stage['description'],
                'action': evolution_stage['action'],
                'impact': evolution_stage['impact']
            })
            
        return suggestions
        
    def _determine_evolution_stage(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Determine NOVA's evolution stage with the user"""
        interactions = user_profile.total_interactions
        
        stages = [
            {
                'threshold': 0,
                'name': 'Initial Setup',
                'next_milestone': 'Basic Assistant',
                'description': 'NOVA is learning your preferences',
                'action': 'Continue using NOVA for various tasks',
                'impact': 'Build personalized AI experience'
            },
            {
                'threshold': 10,
                'name': 'Basic Assistant',
                'next_milestone': 'Productivity Partner',
                'description': 'NOVA understands your basic patterns',
                'action': 'Try more complex tasks and automation',
                'impact': 'Unlock advanced capabilities'
            },
            {
                'threshold': 50,
                'name': 'Productivity Partner',
                'next_milestone': 'AI Co-founder',
                'description': 'NOVA can anticipate your needs',
                'action': 'Enable proactive suggestions and automation',
                'impact': 'Work 2x faster with AI assistance'
            },
            {
                'threshold': 200,
                'name': 'AI Co-founder',
                'next_milestone': 'Synchronized Intelligence',
                'description': 'NOVA deeply understands your work style',
                'action': 'Enable full autonomous mode',
                'impact': 'Achieve flow state with AI'
            },
            {
                'threshold': 1000,
                'name': 'Synchronized Intelligence',
                'next_milestone': None,
                'description': 'NOVA is fully evolved with you',
                'action': 'Continue pushing boundaries together',
                'impact': 'Unlimited potential'
            }
        ]
        
        current_stage = stages[0]
        for stage in stages:
            if interactions >= stage['threshold']:
                current_stage = stage
            else:
                break
                
        return current_stage
        
    async def generate_self_improvement_plan(self) -> Dict[str, Any]:
        """Generate a self-improvement plan for NOVA"""
        # Analyze all performance data
        total_requests = self.performance_data['total_requests']
        
        if total_requests < 10:
            return {
                'status': 'learning',
                'message': 'Still gathering data. Use NOVA more to enable self-improvement.',
                'progress': f'{total_requests}/10 interactions'
            }
            
        # Calculate metrics
        success_rate = self.performance_data['successful_requests'] / total_requests
        avg_time = self.performance_data['average_response_time']
        
        # Identify weak areas
        weak_areas = []
        for pattern, stats in self.performance_data['common_patterns'].items():
            if stats['success_rate'] < 0.8:
                weak_areas.append({
                    'area': pattern,
                    'current_performance': stats['success_rate'],
                    'target': 0.9,
                    'improvement_needed': 0.9 - stats['success_rate']
                })
                
        # Create improvement plan
        plan = {
            'status': 'active',
            'current_metrics': {
                'success_rate': success_rate,
                'avg_response_time': avg_time,
                'total_interactions': total_requests
            },
            'target_metrics': {
                'success_rate': 0.95,
                'avg_response_time': 2.0,
                'user_satisfaction': 0.9
            },
            'improvement_areas': weak_areas,
            'recommended_actions': [],
            'timeline': '2 weeks'
        }
        
        # Add specific recommendations
        if success_rate < 0.9:
            plan['recommended_actions'].append({
                'action': 'Download additional specialized models',
                'reason': 'Improve task-specific performance',
                'priority': 'high'
            })
            
        if avg_time > 3.0:
            plan['recommended_actions'].append({
                'action': 'Enable response caching',
                'reason': 'Reduce response time for common queries',
                'priority': 'medium'
            })
            
        if weak_areas:
            plan['recommended_actions'].append({
                'action': f'Focus on improving {weak_areas[0]["area"]} capabilities',
                'reason': f'Current success rate is only {weak_areas[0]["current_performance"]:.1%}',
                'priority': 'high'
            })
            
        # Track evolution
        self.performance_data['evolution_timeline'].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': plan['current_metrics'],
            'plan': plan['recommended_actions']
        })
        
        self.save_performance_data()
        
        return plan
        
    async def predict_user_needs(self, user_profile: UserProfile, 
                                current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict what the user might need based on patterns"""
        predictions = []
        
        # Time-based predictions
        current_hour = datetime.now().hour
        
        if user_profile.preferences.working_hours:
            work_start, work_end = user_profile.preferences.working_hours.split('-')
            work_start_hour = int(work_start.split(':')[0])
            work_end_hour = int(work_end.split(':')[0])
            
            if current_hour == work_start_hour:
                predictions.append({
                    'type': 'daily_routine',
                    'prediction': 'Starting work day',
                    'suggestion': 'Would you like me to prepare your development environment?',
                    'confidence': 0.8
                })
                
        # Project-based predictions
        if user_profile.recent_projects:
            last_project = user_profile.recent_projects[-1]
            predictions.append({
                'type': 'project_continuation',
                'prediction': f'Continue work on {last_project}',
                'suggestion': f'Resume {last_project}? I can open the project and show recent changes.',
                'confidence': 0.7
            })
            
        # Pattern-based predictions
        patterns = self.performance_data['common_patterns']
        most_common = max(patterns.items(), key=lambda x: x[1]['count']) if patterns else None
        
        if most_common:
            pattern_type = most_common[0]
            predictions.append({
                'type': 'common_task',
                'prediction': f'You often need {pattern_type}',
                'suggestion': f'Need help with {pattern_type} today?',
                'confidence': 0.6
            })
            
        return predictions
        
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status"""
        return {
            'performance_data': self.performance_data,
            'recent_insights': self.learning_insights[-10:],
            'suggestions_available': len(self.suggestions_made),
            'evolution_progress': self._calculate_evolution_progress()
        }
        
    def _calculate_evolution_progress(self) -> float:
        """Calculate overall evolution progress (0-100%)"""
        factors = []
        
        # Success rate factor
        if self.performance_data['total_requests'] > 0:
            success_rate = self.performance_data['successful_requests'] / self.performance_data['total_requests']
            factors.append(success_rate * 100)
            
        # Response time factor (inverse)
        avg_time = self.performance_data['average_response_time']
        if avg_time > 0:
            time_score = min(100, (2.0 / avg_time) * 100)  # 2s is ideal
            factors.append(time_score)
            
        # Model diversity factor
        models_used = len(self.performance_data['model_performance'])
        diversity_score = min(100, models_used * 20)  # 5+ models = 100%
        factors.append(diversity_score)
        
        # Learning factor
        insights_generated = len(self.learning_insights)
        learning_score = min(100, insights_generated * 10)  # 10+ insights = 100%
        factors.append(learning_score)
        
        return sum(factors) / len(factors) if factors else 0.0