"""
Document Intelligence System - Main Processing Module
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging
from pathlib import Path

from src.document_processor import DocumentProcessor
from src.persona_analyzer import PersonaAnalyzer
from src.relevance_ranker import RelevanceRanker
from src.section_extractor import SectionExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIntelligenceSystem:
    """Main orchestrator for the document intelligence pipeline"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.persona_analyzer = PersonaAnalyzer()
        self.relevance_ranker = RelevanceRanker()
        self.section_extractor = SectionExtractor()
        
    def process_collection(self, input_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        Process a document collection based on input specification
        
        Args:
            input_path: Path to the input JSON file
            output_path: Path for output JSON file (optional)
            
        Returns:
            Dictionary containing the processed results
        """
        start_time = time.time()
        
        # Load input specification
        with open(input_path, 'r', encoding='utf-8') as f:
            input_spec = json.load(f)
            
        logger.info(f"Processing collection: {input_spec['challenge_info']['description']}")
        
        # Extract PDF directory path
        input_dir = Path(input_path).parent
        pdf_dir = input_dir / "PDFs"
        
        # Extract persona and job information
        persona = input_spec.get('persona', {}).get('role', '')
        job_task = input_spec.get('job_to_be_done', {}).get('task', '')
        document_list = input_spec.get('documents', [])
        
        logger.info(f"Persona: {persona}")
        logger.info(f"Job: {job_task}")
        logger.info(f"Documents: {len(document_list)}")
        
        # Process documents
        processed_docs = []
        for doc_info in document_list:
            doc_filename = doc_info.get('filename', '')
            doc_path = pdf_dir / doc_filename
            
            if doc_path.exists():
                logger.info(f"Processing: {doc_filename}")
                doc_content = self.document_processor.extract_text_and_structure(str(doc_path))
                processed_docs.append({
                    'filename': doc_filename,
                    'content': doc_content
                })
            else:
                logger.warning(f"Document not found: {doc_path}")
        
        # Analyze persona context
        persona_context = self.persona_analyzer.create_persona_profile(persona, job_task)
        
        # Extract and rank sections
        section_candidates = []
        for doc in processed_docs:
            sections = self.section_extractor.extract_sections(
                doc['content'], 
                doc['filename']
            )
            section_candidates.extend(sections)
        
        # Rank sections based on persona and job relevance
        ranked_sections = self.relevance_ranker.rank_sections(
            section_candidates,
            persona_context,
            job_task
        )
        
        # Select top sections
        top_sections = ranked_sections[:5]  # Top 5 sections
        
        # Extract subsections for detailed analysis
        subsections = []
        for section in top_sections:
            sub_analysis = self.section_extractor.extract_subsections(
                section,
                persona_context,
                job_task
            )
            subsections.extend(sub_analysis)
        
        # Prepare output
        output_data = {
            "metadata": {
                "input_documents": [doc['filename'] for doc in processed_docs],
                "persona": persona,
                "job_to_be_done": job_task,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [
                {
                    "document": section['document'],
                    "section_title": section['title'],
                    "importance_rank": idx + 1,
                    "page_number": section['page_number']
                }
                for idx, section in enumerate(top_sections)
            ],
            "subsection_analysis": [
                {
                    "document": sub['document'],
                    "refined_text": sub['content'],
                    "page_number": sub['page_number']
                }
                for sub in subsections[:5]  # Top 5 subsections
            ]
        }
        
        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        # Save output if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Results saved to: {output_path}")
        
        return output_data
    
    def batch_process(self, collections_dir: str):
        """Process multiple collections in batch"""
        collections_path = Path(collections_dir)
        
        for collection_dir in collections_path.iterdir():
            if collection_dir.is_dir():
                input_file = collection_dir / "challenge1b_input.json"
                output_file = collection_dir / "challenge1b_output_generated.json"
                
                if input_file.exists():
                    logger.info(f"Processing collection: {collection_dir.name}")
                    try:
                        self.process_collection(str(input_file), str(output_file))
                    except Exception as e:
                        logger.error(f"Error processing {collection_dir.name}: {str(e)}")

def main():
    """Main entry point"""
    system = DocumentIntelligenceSystem()
    
    # Process all collections
    base_dir = Path(__file__).parent
    collections_dir = base_dir
    
    # Look for Collection directories
    for item in collections_dir.iterdir():
        if item.is_dir() and item.name.startswith("Collection"):
            input_file = item / "challenge1b_input.json"
            output_file = item / "challenge1b_output_generated.json"
            
            if input_file.exists():
                logger.info(f"Processing {item.name}")
                try:
                    system.process_collection(str(input_file), str(output_file))
                except Exception as e:
                    logger.error(f"Error processing {item.name}: {str(e)}")

if __name__ == "__main__":
    main()
