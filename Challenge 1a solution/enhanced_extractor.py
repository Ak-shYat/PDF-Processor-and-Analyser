import fitz  # PyMuPDF
import re
from collections import defaultdict
import math

def extract_pdf_features(pdf_path):
    doc = fitz.open(pdf_path)
    features = []
    page_text_stats = {}

    for page_num, page in enumerate(doc, start=1):
        page_dict = page.get_text("dict")
        blocks = page_dict["blocks"]
        
        # Calculate page statistics for better normalization
        page_fonts = []
        page_positions = []
        
        for block in blocks:
            if 'lines' not in block:
                continue
            
            for line in block['lines']:
                line_text = ""
                line_fonts = []
                line_flags = []
                line_bbox = line['bbox']
                
                for span in line['spans']:
                    if span['text'].strip():
                        line_text += span['text']
                        line_fonts.append(span['size'])
                        line_flags.append(span['flags'])
                        page_fonts.append(span['size'])
                        page_positions.append(span['bbox'][1])  # Y position
                
                if line_text.strip():
                    # Calculate line-level features
                    avg_font_size = sum(line_fonts) / len(line_fonts) if line_fonts else 0
                    is_bold = any(flag & 2**4 for flag in line_flags)  # Bold flag
                    is_italic = any(flag & 2**1 for flag in line_flags)  # Italic flag
                    
                    # Position features
                    x_start = line_bbox[0]
                    y_start = line_bbox[1]
                    line_width = line_bbox[2] - line_bbox[0]
                    line_height = line_bbox[3] - line_bbox[1]
                    
                    # Text features
                    text_clean = clean_text(line_text)
                    word_count = len(text_clean.split())
                    char_count = len(text_clean)
                    
                    features.append({
                        'text': text_clean,
                        'font_size': avg_font_size,
                        'bold': is_bold,
                        'italic': is_italic,
                        'x': x_start,
                        'y': y_start,
                        'width': line_width,
                        'height': line_height,
                        'word_count': word_count,
                        'char_count': char_count,
                        'page': page_num,
                        'line_bbox': line_bbox
                    })
        
        # Store page-level statistics
        if page_fonts:
            page_text_stats[page_num] = {
                'avg_font_size': sum(page_fonts) / len(page_fonts),
                'max_font_size': max(page_fonts),
                'min_font_size': min(page_fonts),
                'font_std': calculate_std(page_fonts),
                'avg_y_position': sum(page_positions) / len(page_positions) if page_positions else 0,
                'page_height': page.rect.height,
                'page_width': page.rect.width
            }
    
    # Add relative features based on page statistics
    for feature in features:
        page_num = feature['page']
        if page_num in page_text_stats:
            stats = page_text_stats[page_num]
            feature['font_size_ratio'] = feature['font_size'] / stats['avg_font_size'] if stats['avg_font_size'] > 0 else 1
            feature['relative_y_position'] = feature['y'] / stats['page_height'] if stats['page_height'] > 0 else 0
            feature['relative_x_position'] = feature['x'] / stats['page_width'] if stats['page_width'] > 0 else 0
    
    return features, page_text_stats

def clean_text(text):
    """Enhanced text cleaning"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove standalone punctuation
    text = re.sub(r'^\W+$', '', text)
    
    # Remove very short fragments (likely OCR errors)
    if len(text) < 2:
        return ""
    
    return text

def calculate_std(values):
    """Calculate standard deviation"""
    if len(values) < 2:
        return 0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def detect_text_patterns(text):
    """Detect if text follows heading patterns"""
    patterns = {
        'numbered_section': r'^\d+\.?\s+[A-Z]',  # "1. Introduction"
        'lettered_section': r'^[A-Z]\.?\s+[A-Z]',  # "A. Overview"
        'roman_numerals': r'^[IVX]+\.?\s+[A-Z]',  # "I. Introduction"
        'all_caps': r'^[A-Z\s\d\.\-]+$',  # "INTRODUCTION"
        'title_case': r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # "Introduction to AI"
        'chapter_keywords': r'^(Chapter|Section|Part|Appendix|Introduction|Conclusion|Summary|Abstract|Overview)\b',
    }
    
    detected_patterns = []
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            detected_patterns.append(pattern_name)
    
    return detected_patterns

def is_likely_heading(feature, page_stats):
    """Advanced heading detection using multiple features"""
    score = 0
    
    # Font size features
    if feature['font_size_ratio'] > 1.2:  # Larger than average
        score += 2
    elif feature['font_size_ratio'] > 1.1:
        score += 1
    
    # Bold text
    if feature['bold']:
        score += 2
    
    # Position features
    if feature['relative_y_position'] < 0.1:  # Top of page
        score += 1
    
    if feature['relative_x_position'] < 0.1:  # Left aligned
        score += 1
    
    # Text length features
    if 3 <= feature['word_count'] <= 8:  # Typical heading length
        score += 1
    elif feature['word_count'] > 15:  # Too long for heading
        score -= 2
    
    # Pattern matching
    patterns = detect_text_patterns(feature['text'])
    if patterns:
        score += len(patterns)
    
    # Check for common heading words
    heading_keywords = ['introduction', 'conclusion', 'summary', 'abstract', 'overview', 
                       'methodology', 'results', 'discussion', 'background', 'literature']
    if any(keyword in feature['text'].lower() for keyword in heading_keywords):
        score += 1
    
    return score >= 3  # Threshold for heading detection

def remove_duplicates(features):
    """Remove duplicate or very similar text entries"""
    seen = set()
    unique_features = []
    
    for feature in features:
        # Create a normalized key for comparison
        key = (
            feature['text'].lower().strip(),
            feature['page'],
            round(feature['y'], 1)  # Round Y position to handle minor variations
        )
        
        if key not in seen:
            seen.add(key)
            unique_features.append(feature)
    
    return unique_features
