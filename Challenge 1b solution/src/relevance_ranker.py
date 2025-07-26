"""
Relevance Ranker - Advanced similarity-based ranking system for sections
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class RelevanceRanker:
    """Advanced ranking system using multiple similarity algorithms"""
    
    def __init__(self):
        # Initialize lightweight transformer model
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')  # ~80MB model
            logger.info("Loaded sentence transformer model")
        except Exception as e:
            logger.warning(f"Could not load sentence transformer: {e}")
            self.sentence_model = None
        
        # TF-IDF vectorizer for statistical analysis
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        # Similarity weights for different algorithms
        self.similarity_weights = {
            'semantic': 0.4,      # Sentence transformer similarity
            'tfidf': 0.3,         # TF-IDF cosine similarity
            'keyword': 0.2,       # Keyword matching
            'structural': 0.1     # Structural features
        }
    
    def rank_sections(self, sections: List[Dict[str, Any]], persona_context: Dict[str, Any],
                     job_task: str) -> List[Dict[str, Any]]:
        """
        Rank sections based on relevance to persona and job
        """
        if not sections:
            return []
        
        logger.info(f"Ranking {len(sections)} sections")
        
        # Create query context from persona and job
        query_context = self._create_query_context(persona_context, job_task)
        
        # Calculate different similarity scores
        semantic_scores = self._calculate_semantic_similarity(sections, query_context)
        tfidf_scores = self._calculate_tfidf_similarity(sections, query_context)
        keyword_scores = self._calculate_keyword_similarity(sections, persona_context)
        structural_scores = self._calculate_structural_scores(sections, persona_context)
        
        # Combine scores
        final_scores = []
        for i, section in enumerate(sections):
            combined_score = (
                semantic_scores[i] * self.similarity_weights['semantic'] +
                tfidf_scores[i] * self.similarity_weights['tfidf'] +
                keyword_scores[i] * self.similarity_weights['keyword'] +
                structural_scores[i] * self.similarity_weights['structural']
            )
            
            # Apply persona-specific boosting
            boosted_score = self._apply_persona_boosting(
                section, combined_score, persona_context, job_task
            )
            
            final_scores.append(boosted_score)
            section['relevance_score'] = boosted_score
        
        # Sort by relevance score
        ranked_sections = sorted(
            zip(sections, final_scores), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        result = [section for section, _ in ranked_sections]
        
        logger.info(f"Top section: {result[0]['title'][:50]}... (score: {final_scores[0]:.3f})")
        
        return result
    
    def _create_query_context(self, persona_context: Dict[str, Any], job_task: str) -> str:
        """Create query context by combining persona and job information"""
        context_parts = [
            persona_context.get('persona', ''),
            job_task,
            ' '.join(persona_context.get('domain_keywords', [])),
            ' '.join(persona_context.get('job_actions', [])),
            ' '.join(persona_context.get('priority_areas', []))
        ]
        
        # Add requirements
        requirements = persona_context.get('requirements', {})
        context_parts.extend(requirements.get('dietary', []))
        context_parts.extend(requirements.get('special_needs', []))
        
        return ' '.join([part for part in context_parts if part])
    
    def _calculate_semantic_similarity(self, sections: List[Dict[str, Any]], 
                                     query_context: str) -> List[float]:
        """Calculate semantic similarity using sentence transformers"""
        if not self.sentence_model:
            return [0.5] * len(sections)  # Fallback neutral score
        
        try:
            # Get embeddings for query context
            query_embedding = self.sentence_model.encode([query_context])
            
            # Get embeddings for all sections
            section_texts = [section['content'] for section in sections]
            section_embeddings = self.sentence_model.encode(section_texts)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_embedding, section_embeddings)[0]
            
            return similarities.tolist()
            
        except Exception as e:
            logger.warning(f"Error in semantic similarity calculation: {e}")
            return [0.5] * len(sections)
    
    def _calculate_tfidf_similarity(self, sections: List[Dict[str, Any]], 
                                  query_context: str) -> List[float]:
        """Calculate TF-IDF cosine similarity"""
        try:
            # Prepare documents
            section_texts = [section['content'] for section in sections]
            all_texts = [query_context] + section_texts
            
            # Fit TF-IDF and transform
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculate similarities (query is first document)
            query_vector = tfidf_matrix[0]
            section_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(query_vector, section_vectors)[0]
            
            return similarities.tolist()
            
        except Exception as e:
            logger.warning(f"Error in TF-IDF similarity calculation: {e}")
            return [0.5] * len(sections)
    
    def _calculate_keyword_similarity(self, sections: List[Dict[str, Any]], 
                                    persona_context: Dict[str, Any]) -> List[float]:
        """Calculate keyword-based similarity using Jaccard coefficient"""
        # Collect all relevant keywords
        keywords = set()
        keywords.update([kw.lower() for kw in persona_context.get('domain_keywords', [])])
        keywords.update([kw.lower() for kw in persona_context.get('job_actions', [])])
        keywords.update([kw.lower() for kw in persona_context.get('priority_areas', [])])
        
        # Add requirement keywords
        requirements = persona_context.get('requirements', {})
        keywords.update([kw.lower() for kw in requirements.get('dietary', [])])
        keywords.update([kw.lower() for kw in requirements.get('special_needs', [])])
        
        similarities = []
        for section in sections:
            section_text = section['content'].lower()
            section_words = set(re.findall(r'\b\w+\b', section_text))
            
            # Calculate Jaccard similarity
            intersection = keywords.intersection(section_words)
            union = keywords.union(section_words)
            
            if union:
                jaccard_sim = len(intersection) / len(union)
            else:
                jaccard_sim = 0
            
            # Also calculate keyword density
            keyword_count = sum(1 for kw in keywords if kw in section_text)
            keyword_density = keyword_count / len(section_text.split()) if section_text.split() else 0
            
            # Combine Jaccard and density
            combined_sim = (jaccard_sim * 0.7) + (min(keyword_density * 10, 1.0) * 0.3)
            similarities.append(combined_sim)
        
        return similarities
    
    def _calculate_structural_scores(self, sections: List[Dict[str, Any]], 
                                   persona_context: Dict[str, Any]) -> List[float]:
        """Calculate scores based on structural features"""
        scores = []
        
        for section in sections:
            content = section['content']
            score = 0.0
            
            # Length appropriateness (prefer moderate length)
            length = len(content)
            if 200 <= length <= 1000:
                score += 0.3
            elif 100 <= length <= 1500:
                score += 0.2
            elif length > 50:
                score += 0.1
            
            # Structure indicators
            if ':' in content:  # Likely has definitions or explanations
                score += 0.2
            
            if re.search(r'\d+\.', content):  # Has numbered lists
                score += 0.2
            
            if any(bullet in content for bullet in ['•', '-', '*']):  # Has bullet points
                score += 0.15
            
            # Information density
            info_indicators = ['ingredients', 'steps', 'instructions', 'how to', 'recipe', 
                             'procedure', 'method', 'technique', 'tip', 'recommendation']
            info_count = sum(1 for indicator in info_indicators if indicator in content.lower())
            score += min(info_count * 0.05, 0.3)
            
            # Persona-specific structural preferences
            persona_type = persona_context.get('persona_type', '')
            
            if persona_type == 'contractor' and any(word in content.lower() 
                                                   for word in ['recipe', 'ingredients', 'cooking']):
                score += 0.2
            
            if persona_type == 'planner' and any(word in content.lower() 
                                               for word in ['activity', 'visit', 'explore', 'enjoy']):
                score += 0.2
            
            if persona_type == 'professional' and any(word in content.lower() 
                                                    for word in ['form', 'process', 'step', 'create']):
                score += 0.2
            
            scores.append(min(score, 1.0))  # Cap at 1.0
        
        return scores
    
    def _apply_persona_boosting(self, section: Dict[str, Any], base_score: float,
                              persona_context: Dict[str, Any], job_task: str) -> float:
        """Apply persona-specific boosting to scores"""
        boosted_score = base_score
        content = section['content'].lower()
        persona_type = persona_context.get('persona_type', '')
        
        # Persona-specific boosting
        if persona_type == 'contractor':
            # Boost food/recipe content
            if any(word in content for word in ['recipe', 'ingredients', 'cooking', 'preparation']):
                boosted_score *= 1.3
            
            # Boost dietary requirement mentions
            dietary_reqs = persona_context.get('requirements', {}).get('dietary', [])
            for req in dietary_reqs:
                if req.lower() in content:
                    boosted_score *= 1.2
        
        elif persona_type == 'planner':
            # Boost activity and destination content
            if any(word in content for word in ['activity', 'attraction', 'visit', 'explore', 'destination']):
                boosted_score *= 1.3
            
            # Boost group-related content
            if any(word in content for word in ['group', 'friends', 'together', 'party']):
                boosted_score *= 1.2
        
        elif persona_type == 'professional':
            # Boost process and form content
            if any(word in content for word in ['form', 'process', 'procedure', 'workflow', 'step']):
                boosted_score *= 1.3
            
            # Boost compliance/professional content
            if any(word in content for word in ['compliance', 'professional', 'business', 'corporate']):
                boosted_score *= 1.2
        
        # Job-specific boosting
        job_lower = job_task.lower()
        
        if 'buffet' in job_lower and 'buffet' in content:
            boosted_score *= 1.3
        
        if 'vegetarian' in job_lower and 'vegetarian' in content:
            boosted_score *= 1.3
        
        if 'college' in job_lower and any(word in content for word in ['budget', 'affordable', 'cheap', 'student']):
            boosted_score *= 1.2
        
        if 'corporate' in job_lower and any(word in content for word in ['professional', 'business', 'corporate']):
            boosted_score *= 1.2
        
        # Title relevance boosting
        title = section.get('title', '').lower()
        title_words = set(title.split())
        persona_words = set(persona_context.get('domain_keywords', []))
        
        title_overlap = len(title_words.intersection({w.lower() for w in persona_words}))
        if title_overlap > 0:
            boosted_score *= (1.0 + title_overlap * 0.1)
        
        return min(boosted_score, 2.0)  # Cap boost at 2x
