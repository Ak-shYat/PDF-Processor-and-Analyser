"""
Document Processor - Handles PDF text extraction and structure analysis
"""
import fitz  
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes PDF documents and extracts structured content"""
    
    def __init__(self):
        self.section_patterns = [
            r'^([A-Z][A-Za-z\s]{2,50}):?\s*$',  # Title case headers
            r'^([A-Z\s]{3,50}):?\s*$',           # All caps headers
            r'^\d+\.\s+([A-Za-z\s]{3,50}):?\s*$', # Numbered sections
            r'^([A-Za-z\s]{3,50})\s*-\s*',       # Dash separated
            r'^\*\*([A-Za-z\s]{3,50})\*\*',      # Bold markdown
        ]
        
    def extract_text_and_structure(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text and structure from PDF
        """
        try:
            doc = fitz.open(pdf_path)
            pages_content = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text blocks with position info
                blocks = page.get_text("dict")
                page_text = ""
                sections = []
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                line_text += span["text"]
                            
                            if line_text.strip():
                                page_text += line_text.strip() + "\n"
                                
                                # Check if line might be a section header
                                if self._is_section_header(line_text.strip()):
                                    sections.append({
                                        'title': line_text.strip(),
                                        'position': line["bbox"],
                                        'page': page_num + 1
                                    })
                
                pages_content.append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'sections': sections
                })
            
            doc.close()
            
            return {
                'total_pages': len(pages_content),
                'pages': pages_content,
                'full_text': '\n'.join([p['text'] for p in pages_content])
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return {'total_pages': 0, 'pages': [], 'full_text': ''}
    
    def _is_section_header(self, text: str) -> bool:
        """Check if text line is likely a section header"""
        text = text.strip()
        
        # Too short or too long
        if len(text) < 3 or len(text) > 100:
            return False
            
        # Check against patterns
        for pattern in self.section_patterns:
            if re.match(pattern, text):
                return True
                
        # Additional heuristics
        if (text.isupper() and len(text.split()) <= 8 and 
            not text.endswith('.') and ':' not in text):
            return True
            
        # Title case check
        if (text.istitle() and len(text.split()) <= 10 and 
            not text.endswith('.') and text.count(':') <= 1):
            return True
            
        return False
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for processing
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, start + chunk_size//2, -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'length': len(chunk_text)
                })
            
            start = end - overlap
            
        return chunks
