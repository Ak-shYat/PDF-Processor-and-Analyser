"""
Section Extractor - Extracts and processes document sections and subsections
"""
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class SectionExtractor:
    """Extracts meaningful sections and subsections from processed documents"""
    
    def __init__(self):
        self.min_section_length = 50
        self.max_section_length = 2000
        self.min_subsection_length = 100
        self.max_subsections_per_section = 3
        
    def extract_sections(self, doc_content: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """
        Extract sections from document content
        """
        sections = []
        pages = doc_content.get('pages', [])
        
        for page in pages:
            page_number = page['page_number']
            page_text = page['text']
            page_sections = page.get('sections', [])
            
            # If explicit sections were found
            if page_sections:
                for section in page_sections:
                    section_content = self._extract_section_content(
                        page_text, section['title'], page_number
                    )
                    
                    if self._is_valid_section(section_content):
                        sections.append({
                            'document': filename,
                            'title': section['title'],
                            'content': section_content,
                            'page_number': page_number,
                            'type': 'explicit'
                        })
            
            # Also extract implicit sections using content analysis
            implicit_sections = self._extract_implicit_sections(page_text, page_number, filename)
            sections.extend(implicit_sections)
        
        # Remove duplicates and rank by quality
        sections = self._deduplicate_sections(sections)
        sections = self._rank_sections_by_quality(sections)
        
        logger.info(f"Extracted {len(sections)} sections from {filename}")
        return sections
    
    def extract_subsections(self, section: Dict[str, Any], persona_context: Dict[str, Any], 
                          job_task: str) -> List[Dict[str, Any]]:
        """
        Extract relevant subsections from a main section
        """
        content = section['content']
        
        # Split content into potential subsections
        subsection_candidates = self._split_into_subsections(content)
        
        # Score and rank subsections
        scored_subsections = []
        for idx, subsection in enumerate(subsection_candidates):
            if len(subsection.strip()) >= self.min_subsection_length:
                score = self._score_subsection_relevance(
                    subsection, persona_context, job_task
                )
                
                scored_subsections.append({
                    'document': section['document'],
                    'content': subsection.strip(),
                    'page_number': section['page_number'],
                    'relevance_score': score,
                    'subsection_index': idx
                })
        
        # Sort by relevance and return top subsections
        scored_subsections.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_subsections[:self.max_subsections_per_section]
    
    def _extract_section_content(self, page_text: str, section_title: str, 
                               page_number: int) -> str:
        """Extract content for a specific section"""
        lines = page_text.split('\n')
        section_start = -1
        
        # Find section start
        for i, line in enumerate(lines):
            if section_title.lower() in line.lower():
                section_start = i
                break
        
        if section_start == -1:
            return ""
        
        # Extract content until next section or end
        content_lines = []
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            
            # Stop at next section header
            if self._looks_like_header(line) and len(content_lines) > 3:
                break
                
            if line:
                content_lines.append(line)
        
        return ' '.join(content_lines)
    
    def _extract_implicit_sections(self, page_text: str, page_number: int, 
                                 filename: str) -> List[Dict[str, Any]]:
        """Extract sections using content-based heuristics"""
        sections = []
        
        # Split by double newlines (paragraph breaks)
        paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]
        
        current_section = []
        current_title = None
        
        for paragraph in paragraphs:
            # Check if paragraph starts with potential title
            first_line = paragraph.split('\n')[0].strip()
            
            if self._looks_like_header(first_line) and len(current_section) > 0:
                # Save previous section
                if current_title and current_section:
                    section_content = ' '.join(current_section)
                    if self._is_valid_section(section_content):
                        sections.append({
                            'document': filename,
                            'title': current_title,
                            'content': section_content,
                            'page_number': page_number,
                            'type': 'implicit'
                        })
                
                # Start new section
                current_title = first_line
                current_section = [paragraph[len(first_line):].strip()] if len(paragraph) > len(first_line) else []
            else:
                current_section.append(paragraph)
        
        # Add final section
        if current_title and current_section:
            section_content = ' '.join(current_section)
            if self._is_valid_section(section_content):
                sections.append({
                    'document': filename,
                    'title': current_title or f"Section (Page {page_number})",
                    'content': section_content,
                    'page_number': page_number,
                    'type': 'implicit'
                })
        
        return sections
    
    def _split_into_subsections(self, content: str) -> List[str]:
        """Split content into logical subsections"""
        # Try different splitting strategies
        
        # Strategy 1: Split by numbered lists
        numbered_pattern = r'\n\s*\d+\.\s+'
        if re.search(numbered_pattern, content):
            subsections = re.split(numbered_pattern, content)
            if len(subsections) > 1:
                return [s.strip() for s in subsections if s.strip()]
        
        # Strategy 2: Split by bullet points
        bullet_pattern = r'\n\s*[•·-]\s+'
        if re.search(bullet_pattern, content):
            subsections = re.split(bullet_pattern, content)
            if len(subsections) > 1:
                return [s.strip() for s in subsections if s.strip()]
        
        # Strategy 3: Split by topic changes (simple sentence-based)
        sentences = re.split(r'[.!?]+\s+', content)
        if len(sentences) > 10:
            # Group sentences into subsections
            subsections = []
            current_subsection = []
            
            for sentence in sentences:
                current_subsection.append(sentence)
                if len(' '.join(current_subsection)) > 200:
                    subsections.append(' '.join(current_subsection))
                    current_subsection = []
            
            if current_subsection:
                subsections.append(' '.join(current_subsection))
            
            return subsections
        
        # Fallback: Split by length
        if len(content) > self.max_section_length:
            mid_point = len(content) // 2
            # Find nearest sentence boundary
            for i in range(mid_point, min(len(content), mid_point + 100)):
                if content[i] in '.!?':
                    return [content[:i+1].strip(), content[i+1:].strip()]
        
        return [content]
    
    def _score_subsection_relevance(self, subsection: str, persona_context: Dict[str, Any],
                                  job_task: str) -> float:
        """Score subsection relevance to persona and job"""
        score = 0.0
        subsection_lower = subsection.lower()
        
        # Domain keyword matching
        domain_keywords = persona_context.get('domain_keywords', [])
        for keyword in domain_keywords:
            if keyword.lower() in subsection_lower:
                score += 0.1
        
        # Job action matching
        job_actions = persona_context.get('job_actions', [])
        for action in job_actions:
            if action in subsection_lower:
                score += 0.15
        
        # Requirements matching
        requirements = persona_context.get('requirements', {})
        
        # Dietary requirements
        for dietary in requirements.get('dietary', []):
            if dietary.lower() in subsection_lower:
                score += 0.2
        
        # Special needs
        for need in requirements.get('special_needs', []):
            if need.lower() in subsection_lower:
                score += 0.1
        
        # Content type scoring
        context_weights = persona_context.get('context_weight', {})
        
        # Instructional content (recipes, steps, procedures)
        if any(word in subsection_lower for word in ['instructions', 'steps', 'ingredients', 'how to']):
            score += context_weights.get('instructional', 0.3)
        
        # Descriptive content (descriptions, features, details)
        if any(word in subsection_lower for word in ['description', 'features', 'details', 'includes']):
            score += context_weights.get('descriptive', 0.3)
        
        # Length bonus (prefer substantial content)
        length_score = min(len(subsection) / 500.0, 1.0) * 0.1
        score += length_score
        
        return score
    
    def _looks_like_header(self, line: str) -> bool:
        """Check if line looks like a section header"""
        line = line.strip()
        
        if len(line) < 3 or len(line) > 100:
            return False
        
        # Common header patterns
        patterns = [
            r'^[A-Z][a-z\s]+:?\s*$',  # Title case
            r'^[A-Z\s]{3,}:?\s*$',    # All caps
            r'^\d+\.\s+[A-Za-z]',     # Numbered
            r'^[A-Za-z\s]+ - [A-Za-z]', # Dash separated
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _is_valid_section(self, content: str) -> bool:
        """Check if section content is valid"""
        if not content or len(content.strip()) < self.min_section_length:
            return False
        
        if len(content) > self.max_section_length:
            return False
        
        # Check for meaningful content (not just whitespace or repetitive)
        words = content.split()
        if len(set(words)) < len(words) * 0.3:  # Too repetitive
            return False
        
        return True
    
    def _deduplicate_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sections"""
        seen_content = set()
        unique_sections = []
        
        for section in sections:
            # Create a normalized version for comparison
            normalized = re.sub(r'\s+', ' ', section['content'].lower().strip())
            
            if normalized not in seen_content:
                seen_content.add(normalized)
                unique_sections.append(section)
        
        return unique_sections
    
    def _rank_sections_by_quality(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank sections by quality indicators"""
        def quality_score(section):
            content = section['content']
            score = 0
            
            # Length score (prefer moderate length)
            length = len(content)
            if 200 <= length <= 1000:
                score += 2
            elif 100 <= length <= 1500:
                score += 1
            
            # Structure score (prefer well-structured content)
            if any(pattern in content for pattern in [':', '1.', '•', '-']):
                score += 1
            
            # Informativeness score
            info_words = ['how', 'what', 'where', 'when', 'why', 'include', 'contain']
            for word in info_words:
                if word in content.lower():
                    score += 0.5
            
            return score
        
        sections.sort(key=quality_score, reverse=True)
        return sections
