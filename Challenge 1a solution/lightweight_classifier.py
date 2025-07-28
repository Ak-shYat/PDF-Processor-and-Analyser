import re
import math
from collections import Counter

class LightweightHeadingClassifier:
    """
    A lightweight classifier for heading detection using statistical features
    No external ML libraries required - uses statistical analysis
    """
    
    def __init__(self):
        self.heading_keywords = [
            'introduction', 'conclusion', 'summary', 'abstract', 'overview',
            'methodology', 'method', 'results', 'discussion', 'background',
            'literature', 'review', 'analysis', 'findings', 'recommendations',
            'appendix', 'references', 'bibliography', 'acknowledgments',
            'chapter', 'section', 'part', 'subsection', 'definition',
            'objectives', 'goals', 'purpose', 'scope', 'limitations'
        ]
        
        self.stop_words = [
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        ]
    
    def extract_features(self, text, font_size, is_bold, position_features):
        """Extract features for heading classification"""
        features = {}
        
        # Text features
        words = text.lower().split()
        features['word_count'] = len(words)
        features['char_count'] = len(text)
        features['avg_word_length'] = sum(len(word) for word in words) / len(words) if words else 0
        
        # Capitalization features
        features['title_case'] = self._is_title_case(text)
        features['all_caps'] = text.isupper()
        features['first_word_capitalized'] = text[0].isupper() if text else False
        
        # Keyword features
        features['contains_heading_keyword'] = any(keyword in text.lower() for keyword in self.heading_keywords)
        features['keyword_density'] = sum(1 for word in words if word in self.heading_keywords) / len(words) if words else 0
        
        # Pattern features
        features['starts_with_number'] = bool(re.match(r'^\d+\.?\s+', text))
        features['starts_with_letter'] = bool(re.match(r'^[A-Z]\.?\s+', text))
        features['starts_with_roman'] = bool(re.match(r'^[IVX]+\.?\s+', text))
        
        # Formatting features
        features['font_size'] = font_size
        features['is_bold'] = is_bold
        features['relative_font_size'] = position_features.get('font_size_ratio', 1.0)
        
        # Position features
        features['relative_y_position'] = position_features.get('relative_y_position', 0.5)
        features['relative_x_position'] = position_features.get('relative_x_position', 0.0)
        
        # Punctuation features
        features['ends_with_punctuation'] = text.endswith(('.', '!', '?', ':'))
        features['punctuation_ratio'] = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0
        
        return features
    
    def _is_title_case(self, text):
        """Check if text follows title case pattern"""
        words = text.split()
        if not words:
            return False
        
        # First word should be capitalized
        if not words[0][0].isupper():
            return False
        
        # Most non-stop words should be capitalized
        capitalized_count = sum(1 for word in words[1:] if word.lower() not in self.stop_words and word[0].isupper())
        non_stop_count = sum(1 for word in words[1:] if word.lower() not in self.stop_words)
        
        return non_stop_count == 0 or capitalized_count / non_stop_count > 0.7
    
    def calculate_heading_score(self, text, font_size, is_bold, position_features):
        """Calculate likelihood score for text being a heading"""
        features = self.extract_features(text, font_size, is_bold, position_features)
        
        score = 0
        
        # Font size scoring
        if features['relative_font_size'] > 1.3:
            score += 3
        elif features['relative_font_size'] > 1.1:
            score += 2
        elif features['relative_font_size'] > 1.0:
            score += 1
        
        # Bold text
        if features['is_bold']:
            score += 2
        
        # Length scoring (headings are typically concise)
        if 2 <= features['word_count'] <= 8:
            score += 2
        elif features['word_count'] <= 12:
            score += 1
        elif features['word_count'] > 15:
            score -= 2
        
        # Capitalization scoring
        if features['title_case']:
            score += 2
        elif features['all_caps']:
            score += 1
        elif features['first_word_capitalized']:
            score += 1
        
        # Keyword scoring
        if features['contains_heading_keyword']:
            score += 2
        
        # Pattern scoring
        if features['starts_with_number']:
            score += 2
        elif features['starts_with_letter']:
            score += 1
        elif features['starts_with_roman']:
            score += 1
        
        # Position scoring
        if features['relative_y_position'] < 0.1:  # Top of page
            score += 1
        
        if features['relative_x_position'] < 0.05:  # Left aligned
            score += 1
        
        # Punctuation scoring
        if not features['ends_with_punctuation']:
            score += 1  # Headings typically don't end with punctuation
        
        if features['punctuation_ratio'] < 0.1:
            score += 1  # Headings have less punctuation
        
        return score
    
    def classify_heading_levels(self, headings_with_scores):
        """Classify headings into H1, H2, H3 levels"""
        if not headings_with_scores:
            return []
        
        # Sort by score (descending) and font size (descending)
        sorted_headings = sorted(headings_with_scores, 
                               key=lambda x: (-x['score'], -x['font_size'], x['page'], x['y']))
        
        # Group by similar characteristics
        level_assignments = {}
        used_levels = set()
        
        for heading in sorted_headings:
            # Create signature for grouping
            signature = (
                round(heading['font_size'], 1),
                heading['is_bold'],
                round(heading.get('relative_x_position', 0), 1)
            )
            
            if signature not in level_assignments:
                # Assign next available level
                if 'H1' not in used_levels:
                    level_assignments[signature] = 'H1'
                    used_levels.add('H1')
                elif 'H2' not in used_levels:
                    level_assignments[signature] = 'H2'
                    used_levels.add('H2')
                elif 'H3' not in used_levels:
                    level_assignments[signature] = 'H3'
                    used_levels.add('H3')
                else:
                    level_assignments[signature] = 'H3'  # Default to H3
        
        # Apply level assignments
        result = []
        for heading in sorted_headings:
            signature = (
                round(heading['font_size'], 1),
                heading['is_bold'],
                round(heading.get('relative_x_position', 0), 1)
            )
            
            result.append({
                'level': level_assignments[signature],
                'text': heading['text'],
                'page': heading['page'],
                'score': heading['score']
            })
        
        # Sort by page and position
        result.sort(key=lambda x: (x['page'], next(h['y'] for h in headings_with_scores 
                                                 if h['text'] == x['text'] and h['page'] == x['page'])))
        
        return result
