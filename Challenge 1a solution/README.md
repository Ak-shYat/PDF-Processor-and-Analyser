# Challenge 1a: PDF Processing Solution

## Overview
This is a solution for Challenge 1a of the Adobe India Hackathon 2025. The challenge requires implementing a PDF processing solution that extracts structured data from PDF documents and outputs JSON files. The solution must be containerized using Docker and meet specific performance and resource constraints.

## Challenge Guidelines

### Submission Requirements
- **GitHub Project**: Complete code repository with working solution
- **Dockerfile**: Must be present in the root directory and functional
- **README.md**:  Documentation explaining the solution, models, and libraries used

### Build Command
```bash
docker build -t challenge-1a-solution .
```

### Run Command
```bash
docker run -v "$(pwd)/input":/app/input -v "$(pwd)/output":/app/output challenge-1a-solution
```

### Critical Constraints
- **Execution Time**: ≤ 10 seconds for a 50-page PDF
- **Model Size**: ≤ 200MB (if using ML models)
- **Network**: No internet access allowed during runtime execution
- **Runtime**: Must run on CPU (amd64) with 8 CPUs and 16 GB RAM
- **Architecture**: Must work on AMD64, not ARM-specific

### Key Requirements
- **Automatic Processing**: Process all PDFs from `/app/input` directory
- **Output Format**: Generate `filename.json` for each `filename.pdf`
- **Input Directory**: Read-only access only
- **Open Source**: All libraries, models, and tools must be open source
- **Cross-Platform**: Test on both simple and complex PDFs


## Implementation

This repository contains a robust solution for extracting structured outlines (title, headings, subheadings) from PDF documents. The solution is designed for the Adobe India Hackathon 2025 and meets all challenge requirements, including Dockerization, offline execution, and resource constraints.

### Key Features
- **Automatic PDF scanning** from `/app/input` (or `input/` locally)
- **Advanced text extraction** using PyMuPDF (`fitz`)
- **Heading detection** with a lightweight statistical classifier
- **Strict filtering** to ensure only true headings/subheadings are included
- **JSON output** in the required schema, written to `/app/output` (or `output/` locally)
- **Docker-ready** and works fully offline

### Project Structure
```
Challenge 1a solution/
├── input/               # Place your PDFs here for processing
├── output/              # Processed JSONs will appear here
├── Dockerfile           # Docker container configuration
├── requirements.txt     # All Python dependencies
├── main.py              # Main processing script (entrypoint)
├── enhanced_extractor.py # PDF feature extraction logic
├── lightweight_classifier.py # Heading classifier logic
├── json_writer.py       # Output writer utility
└── README.md            # This file
```

## How to Run Locally

### 1. Install Dependencies (Local Testing)
```bash
pip install -r requirements.txt
```

### 2. Place PDFs for Processing
- Put your PDF files in the `input/` directory (or mount `/app/input` in Docker).

### 3. Run the Script Locally
```bash
python main.py
```
- Output JSONs will appear in the `output/` directory.

## Output Format

Each PDF generates a JSON file matching the schema given below:

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Section Heading", "page": 1 },
    { "level": "H2", "text": "Subsection Heading", "page": 2 }
    // ...
  ]
}
```

## Implementation Details

- **Text Extraction**: Uses PyMuPDF (`fitz`) for robust, layout-aware extraction.
- **Heading Detection**: Combines font size, boldness, position, and text patterns. Only text with high heading scores, large font, and short length is included.
- **Filtering**: Excludes normal text, form fields, and labels. Only true headings/subheadings are output.
- **Performance**: Optimized for ≤10s processing of 50-page PDFs, ≤200MB model size, and no network access.


## Dependencies

All dependencies are listed in `requirements.txt`:
- pymupdf
- numpy
- scikit-learn
- pandas
