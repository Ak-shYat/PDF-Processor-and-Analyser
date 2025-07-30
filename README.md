This repository contains our approach for Challenges 1a and 1b of the Adobe India Hackathon 2025. It provides a containerized PDF processing tool for Challenge 1a and a persona-driven document intelligence system for Challenge 1b, both designed to be efficient, lightweight, and fully functional offline.

## Challenge 1a: PDF Processing Solution

### Overview

A tool that extracts structured outlines (titles, headings, subheadings) from PDF documents and outputs them as JSON files, optimized for performance and containerized for consistent execution.

### Key Features

- **Automatic PDF Processing**: Scans all PDFs in the `/app/input` directory (or `input/` locally).
- **Advanced Text Extraction**: Utilizes PyMuPDF for robust, layout-aware text extraction.
- **Heading Detection**: Employs a lightweight statistical classifier to identify headings and subheadings.
- **JSON Output**: Generates structured JSON files with document titles and outlines, saved to `/app/output` (or `output/` locally).
- **Dockerized**: Fully containerized for execution on AMD64 CPUs.
- **Offline Operation**: No internet access required during runtime.

### Project Structure

```
Challenge 1a solution/
├── input/               # Place your PDFs here for processing
├── output/              # Processed JSONs will appear here
├── Dockerfile           # Docker container configuration
├── requirements.txt     # Python dependencies
├── main.py              # Main processing script
├── enhanced_extractor.py # PDF feature extraction logic
├── lightweight_classifier.py # Heading classifier logic
├── json_writer.py       # Output writer utility
└── README.md            # This file
```

### Output Format

Each processed PDF generates a JSON file with the following schema:

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Section Heading", "page": 1 },
    { "level": "H2", "text": "Subsection Heading", "page": 2 }
  ]
}
```

### Dependencies

```
pymupdf
numpy
scikit-learn
pandas
```

## Challenge 1b: Persona-Driven Document Intelligence System

### Overview

A sophisticated system that processes document collections to extract and rank pertinent information based on persona-specific requirements, optimized for efficiency and accuracy.

### Key Features

- **Document Processing Pipeline**: Extracts text and structure from PDFs using PyMuPDF, with semantic chunking and section detection.
- **Persona-Aware Similarity Engine**: Combines sentence-transformers and TF-IDF for hybrid semantic-statistical analysis, creating dynamic persona profiles for job alignment scoring.
- **Intelligent Ranking System**: Evaluates relevance using semantic similarity, keyword density, and section importance, with diversity optimization.
- **Advanced Features**: Includes adaptive thresholding, cross-document coherence, and optimized CPU-only execution.
- **Performance**: Processes 3-5 documents in under 60 seconds with a model footprint under 1GB, ensuring high accuracy and scalability.

### Project Structure

```
Challenge 1b solution/
├── Collection 1/
│   ├── challenge1b_input.json
│   └── PDFs/
│       ├── document1.pdf
│       └── document2.pdf
├── Collection 2/
│   ├── challenge1b_input.json
│   └── PDFs/
│       ├── document1.pdf
│       └── document2.pdf
└── Collection 3/
    ├── challenge1b_input.json
    └── PDFs/
        ├── document1.pdf
        └── document2.pdf
```

### Dependencies

```
pymupdf
sentence-transformers
scikit-learn
pandas
numpy
```
