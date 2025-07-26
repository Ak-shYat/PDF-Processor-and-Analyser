"""
Persona Analyzer - Creates persona profiles and job context understanding
"""
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class PersonaAnalyzer:
    """Analyzes persona and job requirements to create contextual profiles"""
    
    def __init__(self):
        # Domain-specific keywords for different personas
        self.persona_keywords = {
            'researcher': ['research', 'methodology', 'analysis', 'study', 'findings', 'literature', 'academic', 'publication', 'data', 'experiment'],
            'student': ['learn', 'study', 'exam', 'concept', 'understanding', 'education', 'knowledge', 'practice', 'tutorial', 'explanation'],
            'analyst': ['analysis', 'trend', 'metrics', 'performance', 'evaluation', 'comparison', 'insight', 'report', 'assessment', 'review'],
            'manager': ['strategy', 'planning', 'coordination', 'team', 'leadership', 'decision', 'execution', 'oversight', 'process', 'management'],
            'planner': ['plan', 'schedule', 'organize', 'coordinate', 'timeline', 'logistics', 'arrangement', 'preparation', 'itinerary', 'booking'],
            'contractor': ['service', 'delivery', 'quality', 'specification', 'requirement', 'standard', 'compliance', 'execution', 'performance', 'contract'],
            'professional': ['expertise', 'skill', 'experience', 'competency', 'qualification', 'practice', 'standard', 'protocol', 'procedure', 'guideline']
        }
        
        # Job-specific action words
        self.job_actions = {
            'create': ['design', 'build', 'develop', 'make', 'construct', 'generate', 'produce', 'establish'],
            'analyze': ['examine', 'evaluate', 'assess', 'review', 'investigate', 'study', 'research', 'compare'],
            'plan': ['organize', 'schedule', 'prepare', 'arrange', 'coordinate', 'design', 'structure', 'outline'],
            'manage': ['oversee', 'supervise', 'control', 'direct', 'handle', 'administer', 'govern', 'lead'],
            'prepare': ['ready', 'setup', 'arrange', 'organize', 'compile', 'assemble', 'gather', 'collect']
        }
        
    def create_persona_profile(self, persona: str, job_task: str) -> Dict[str, Any]:
        """
        Create a comprehensive persona profile
        
        Args:
            persona: Role description
            job_task: Task to be accomplished
            
        Returns:
            Dictionary with persona context and preferences
        """
        persona_lower = persona.lower()
        task_lower = job_task.lower()
        
        # Extract persona type
        persona_type = self._identify_persona_type(persona_lower)
        
        # Extract job actions
        job_actions = self._extract_job_actions(task_lower)
        
        # Get domain keywords
        domain_keywords = self._get_domain_keywords(persona_type, task_lower)
        
        # Extract specific requirements
        requirements = self._extract_requirements(task_lower)
        
        profile = {
            'persona': persona,
            'persona_type': persona_type,
            'job_task': job_task,
            'job_actions': job_actions,
            'domain_keywords': domain_keywords,
            'requirements': requirements,
            'priority_areas': self._identify_priority_areas(persona_type, job_actions),
            'context_weight': self._calculate_context_weights(persona_type, job_actions)
        }
        
        logger.info(f"Created profile for {persona_type} with actions: {', '.join(job_actions)}")
        
        return profile
    
    def _identify_persona_type(self, persona: str) -> str:
        """Identify the primary persona type"""
        for persona_type, keywords in self.persona_keywords.items():
            if persona_type in persona or any(keyword in persona for keyword in keywords[:3]):
                return persona_type
        
        # Fallback classification
        if any(word in persona for word in ['hr', 'human', 'resource']):
            return 'professional'
        elif any(word in persona for word in ['food', 'chef', 'cook', 'menu']):
            return 'contractor'
        elif any(word in persona for word in ['travel', 'trip', 'tour']):
            return 'planner'
        
        return 'professional'
    
    def _extract_job_actions(self, task: str) -> List[str]:
        """Extract key actions from job task"""
        actions = []
        
        for action_type, action_words in self.job_actions.items():
            if action_type in task or any(word in task for word in action_words):
                actions.append(action_type)
        
        # Additional action detection
        if 'menu' in task or 'food' in task or 'recipe' in task:
            actions.append('prepare')
        if 'form' in task or 'document' in task:
            actions.append('create')
        if 'trip' in task or 'travel' in task or 'itinerary' in task:
            actions.append('plan')
        
        return list(set(actions)) if actions else ['analyze']
    
    def _get_domain_keywords(self, persona_type: str, task: str) -> List[str]:
        """Get relevant domain keywords"""
        keywords = self.persona_keywords.get(persona_type, [])
        
        # Add task-specific keywords
        task_keywords = []
        
        # Food domain
        if any(word in task for word in ['menu', 'food', 'recipe', 'vegetarian', 'buffet']):
            task_keywords.extend(['recipe', 'ingredient', 'cooking', 'nutrition', 'dietary'])
        
        # Travel domain
        if any(word in task for word in ['travel', 'trip', 'vacation', 'tourist']):
            task_keywords.extend(['destination', 'activity', 'accommodation', 'transportation', 'attraction'])
        
        # Business domain
        if any(word in task for word in ['business', 'corporate', 'company', 'professional']):
            task_keywords.extend(['business', 'corporate', 'professional', 'service', 'quality'])
        
        # HR/Forms domain
        if any(word in task for word in ['form', 'hr', 'employee', 'onboarding']):
            task_keywords.extend(['form', 'employee', 'process', 'compliance', 'documentation'])
        
        return keywords + task_keywords
    
    def _extract_requirements(self, task: str) -> Dict[str, Any]:
        """Extract specific requirements from task"""
        requirements = {
            'dietary': [],
            'size': None,
            'duration': None,
            'special_needs': []
        }
        
        # Dietary requirements
        dietary_terms = ['vegetarian', 'vegan', 'gluten-free', 'halal', 'kosher', 'dairy-free']
        for term in dietary_terms:
            if term in task:
                requirements['dietary'].append(term)
        
        # Group size
        size_match = re.search(r'(\d+)\s*(people|person|friend|guest|individual)', task)
        if size_match:
            requirements['size'] = int(size_match.group(1))
        
        # Duration
        duration_match = re.search(r'(\d+)\s*(day|week|hour|month)', task)
        if duration_match:
            requirements['duration'] = f"{duration_match.group(1)} {duration_match.group(2)}s"
        
        # Special needs
        if 'corporate' in task:
            requirements['special_needs'].append('professional')
        if 'buffet' in task:
            requirements['special_needs'].append('buffet-style')
        if 'college' in task:
            requirements['special_needs'].append('budget-friendly')
        
        return requirements
    
    def _identify_priority_areas(self, persona_type: str, job_actions: List[str]) -> List[str]:
        """Identify priority focus areas"""
        priority_map = {
            'researcher': ['methodology', 'analysis', 'findings', 'literature'],
            'student': ['concepts', 'examples', 'explanations', 'practice'],
            'planner': ['logistics', 'schedule', 'activities', 'recommendations'],
            'contractor': ['specifications', 'quality', 'delivery', 'requirements'],
            'professional': ['process', 'compliance', 'standards', 'best-practices']
        }
        
        base_priorities = priority_map.get(persona_type, ['information', 'details'])
        
        # Add action-specific priorities
        action_priorities = {
            'create': ['instructions', 'steps', 'tools', 'templates'],
            'plan': ['options', 'schedule', 'logistics', 'recommendations'],
            'analyze': ['data', 'comparison', 'insights', 'trends'],
            'prepare': ['ingredients', 'materials', 'steps', 'requirements']
        }
        
        for action in job_actions:
            base_priorities.extend(action_priorities.get(action, []))
        
        return list(set(base_priorities))
    
    def _calculate_context_weights(self, persona_type: str, job_actions: List[str]) -> Dict[str, float]:
        """Calculate weights for different types of content"""
        weights = {
            'instructional': 0.3,
            'descriptive': 0.3,
            'analytical': 0.2,
            'reference': 0.2
        }
        
        # Adjust based on persona
        if persona_type in ['student', 'researcher']:
            weights['analytical'] += 0.2
            weights['reference'] += 0.1
        elif persona_type in ['planner', 'contractor']:
            weights['instructional'] += 0.2
            weights['descriptive'] += 0.1
        
        # Adjust based on actions
        if 'create' in job_actions or 'prepare' in job_actions:
            weights['instructional'] += 0.2
        if 'analyze' in job_actions:
            weights['analytical'] += 0.2
        if 'plan' in job_actions:
            weights['descriptive'] += 0.2
        
        # Normalize weights
        total_weight = sum(weights.values())
        for key in weights:
            weights[key] = weights[key] / total_weight
        
        return weights
