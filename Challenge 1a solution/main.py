import os
import time
from enhanced_extractor import extract_pdf_features, remove_duplicates
from lightweight_classifier import LightweightHeadingClassifier
from json_writer import write_output

INPUT_DIR = './input'
OUTPUT_DIR = './output'

def process_pdfs_with_ml():
    """Process PDFs using the lightweight ML classifier"""
    
    # Initialize classifier
    classifier = LightweightHeadingClassifier()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(INPUT_DIR, filename)
            print(f"Processing {filename}...")
            
            start_time = time.time()
            
            try:
                # Extract features
                features, page_stats = extract_pdf_features(pdf_path)
                
                # Remove duplicates
                features = remove_duplicates(features)
                
                # Calculate heading scores for all text
                headings_with_scores = []
                for feature in features:
                    score = classifier.calculate_heading_score(
                        feature['text'],
                        feature['font_size'],
                        feature['bold'],
                        feature
                    )

                    avg_font_size = 0
                    if feature.get('font_size_ratio'):
                        avg_font_size = feature['font_size'] / feature['font_size_ratio']
                    else:
                        avg_font_size = feature['font_size']
                    text = feature['text'].strip()
                    word_count = len(text.split())
                    is_heading = (
                        score >= 7 and
                        feature.get('font_size_ratio', 1.0) >= 1.3 and
                        2 <= word_count <= 10 and
                        ':' not in text and
                        not text.endswith('.') and
                        not (text.isupper() and word_count <= 4)
                    )
                    if is_heading:
                        headings_with_scores.append({
                            'text': feature['text'],
                            'font_size': feature['font_size'],
                            'is_bold': feature['bold'],
                            'page': feature['page'],
                            'y': feature['y'],
                            'score': score,
                            'relative_x_position': feature.get('relative_x_position', 0)
                        })
                
                # Determine title
                title = determine_title_ml(features, headings_with_scores)
                
                # Classify heading levels
                outline_with_scores = classifier.classify_heading_levels(headings_with_scores)
                
                # Clean up outline (remove score for final output)
                outline = []
                for item in outline_with_scores:
                    # Support H4 if classifier assigns more than 3 levels
                    level = item['level']
                    if level not in ['H1', 'H2', 'H3', 'H4']:
                        # Fallback to H3 if unknown
                        level = 'H3'
                    outline.append({
                        'level': level,
                        'text': item['text'],
                        'page': item['page']
                    })
                
                # Create final output
                output_json = {
                    'title': title,
                    'outline': outline
                }
                
                # Write output
                output_file = os.path.join(OUTPUT_DIR, filename.replace('.pdf', '.json'))
                write_output(output_json, output_file)
                
                processing_time = time.time() - start_time
                print(f"Generated JSON: {output_file}")
                print(f"  - Title: {output_json['title']}")
                print(f"  - Headings found: {len(output_json['outline'])}")
                print(f"  - Processing time: {processing_time:.2f} seconds")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                # Create minimal output for failed files
                error_output = {
                    "title": f"Error processing {filename}",
                    "outline": []
                }
                output_file = os.path.join(OUTPUT_DIR, filename.replace('.pdf', '.json'))
                write_output(error_output, output_file)

def determine_title_ml(all_features, headings_with_scores):
    """Determine document title using ML approach"""
    
    # Strategy 1: Look for highest scoring heading in top area of first page
    first_page_headings = [h for h in headings_with_scores if h['page'] == 1]
    if first_page_headings:
        # Find headings in top 25% of first page
        top_area_headings = [h for h in first_page_headings 
                           if h.get('relative_y_position', 0) < 0.25]
        if top_area_headings:
            # Get highest scoring heading in top area
            title_candidate = max(top_area_headings, key=lambda x: x['score'])
            return clean_title(title_candidate['text'])
    
    # Strategy 2: Use first heading as title
    if headings_with_scores:
        first_heading = min(headings_with_scores, key=lambda x: (x['page'], x['y']))
        return clean_title(first_heading['text'])
    
    # Strategy 3: Use largest font text from first page
    first_page_features = [f for f in all_features if f['page'] == 1]
    if first_page_features:
        largest_font = max(first_page_features, key=lambda x: x['font_size'])
        return clean_title(largest_font['text'])
    
    return "Unknown Title"

def clean_title(title):
    """Clean title text"""
    import re
    
    title = title.strip()
    
    # Remove common prefixes
    prefixes_to_remove = ['RFP:', 'Request for Proposal:', 'Document:', 'Report:', 'Title:']
    for prefix in prefixes_to_remove:
        if title.upper().startswith(prefix.upper()):
            title = title[len(prefix):].strip()
    
    # Remove numbering at the start
    title = re.sub(r'^\d+\.?\s+', '', title)
    title = re.sub(r'^[A-Z]\.?\s+', '', title)
    
    # If title is too short or just punctuation, return default
    if len(title) < 3 or re.match(r'^\W+$', title):
        return "Unknown Title"
    
    # Limit title length
    if len(title) > 100:
        title = title[:97] + "..."
    
    return title

if __name__ == '__main__':
    process_pdfs_with_ml()
