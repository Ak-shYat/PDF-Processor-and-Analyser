# Challenge 1a: PDF Processing Solution

## Overview
This is a solution for Challenge 1a of the Adobe India Hackathon 2025. The challenge requires implementing a PDF processing solution that extracts structured data from PDF documents and outputs JSON files. The solution must be containerized using Docker and meet specific performance and resource constraints.

## Official Challenge Guidelines

### Submission Requirements
- **GitHub Project**: Complete code repository with working solution
- **Dockerfile**: Must be present in the root directory and functional
- **README.md**:  Documentation explaining the solution, models, and libraries used

### Build Command
```bash
docker build --platform linux/amd64 -t <reponame.someidentifier> .
```

### Run Command
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output/repoidentifier/:/app/output --network none <reponame.someidentifier>
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

## Sample Solution Structure
```
Challenge_1a/
├── sample_dataset/
│   ├── outputs/         # JSON files provided as outputs.
│   ├── pdfs/            # Input PDF files
│   └── schema/          # Output schema definition
│       └── output_schema.json
├── Dockerfile           # Docker container configuration
├── process_pdfs.py      # Sample processing script
└── README.md           # This file
```

## Sample Implementation

## Real Solution Overview

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
Challenge_1a/
├── sample_dataset/
│   ├── outputs/         # Reference JSON outputs
│   ├── pdfs/            # Sample input PDFs
│   └── schema/          # Output schema definition
│       └── output_schema.json
├── input/               # Place your PDFs here for processing
├── output/              # Processed JSONs will appear here
├── Dockerfile           # Docker container configuration
├── requirements.txt     # All Python dependencies
├── process_pdfs.py      # Main processing script (entrypoint)
├── enhanced_extractor.py# PDF feature extraction logic
├── lightweight_classifier.py # Heading classifier logic
├── json_writer.py       # Output writer utility
└── README.md            # This file
```

### Main Components
- `process_pdfs.py`: Orchestrates PDF processing, heading detection, and output.
- `enhanced_extractor.py`: Extracts text, font, and layout features from PDFs using PyMuPDF.
- `lightweight_classifier.py`: Assigns heading scores and levels (H1-H4) using statistical rules.
- `json_writer.py`: Writes output JSON in the required format.

## How to Build and Run

### 1. Install Dependencies (Local Testing)
```bash
pip install -r requirements.txt
```

### 2. Place PDFs for Processing
- Put your PDF files in the `input/` directory (or mount `/app/input` in Docker).

### 3. Run the Script Locally
```bash
python process_pdfs.py
```
- Output JSONs will appear in the `output/` directory.

### 4. Build and Run with Docker
```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-processor .

# Run the container (replace paths as needed)
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none pdf-processor
```

## Output Format

Each PDF generates a JSON file matching the schema in `sample_dataset/schema/output_schema.json`:

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

## Testing & Validation

- Place test PDFs in `input/` and run the script or Docker container.
- Compare output JSONs in `output/` to the reference outputs in `sample_dataset/outputs/`.
- Validate against the schema in `sample_dataset/schema/output_schema.json`.

## Troubleshooting

- If you see too many outline entries, adjust the heading score threshold or filtering logic in `process_pdfs.py`.
- If you see no headings, try lowering the threshold or check your PDF's structure.

## Dependencies

All dependencies are listed in `requirements.txt`:
- pymupdf
- PyPDF2
- numpy
- scikit-learn
- pandas
- pdfminer.six

## Contact
For questions or issues, please open an issue in your repository or contact the project maintainer.

## Expected Output Format

### Required JSON Structure
Each PDF should generate a corresponding JSON file that **must conform to the schema** defined in `sample_dataset/schema/output_schema.json`.


## Implementation Guidelines

### Performance Considerations
- **Memory Management**: Efficient handling of large PDFs
- **Processing Speed**: Optimize for sub-10-second execution
- **Resource Usage**: Stay within 16GB RAM constraint
- **CPU Utilization**: Efficient use of 8 CPU cores

### Testing Strategy
- **Simple PDFs**: Test with basic PDF documents
- **Complex PDFs**: Test with multi-column layouts, images, tables
- **Large PDFs**: Verify 50-page processing within time limit


## Testing Your Solution

### Local Testing
```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-processor .

# Test with sample data
docker run --rm -v $(pwd)/sample_dataset/pdfs:/app/input:ro -v $(pwd)/sample_dataset/outputs:/app/output --network none pdf-processor
```

### Validation Checklist
- [ ] All PDFs in input directory are processed
- [ ] JSON output files are generated for each PDF
- [ ] Output format matches required structure
- [ ] **Output conforms to schema** in `sample_dataset/schema/output_schema.json`
- [ ] Processing completes within 10 seconds for 50-page PDFs
- [ ] Solution works without internet access
- [ ] Memory usage stays within 16GB limit
- [ ] Compatible with AMD64 architecture

---

**Important**: This is a sample implementation. Participants should develop their own solutions that meet all the official challenge requirements and constraints. 