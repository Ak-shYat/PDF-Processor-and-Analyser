# Document Intelligence System - Challenge 1b Solution

## Quick Start with Docker

### 1. Build the Docker Image

```bash
cd "Challenge 1b solution"
docker build -t document-intelligence .
```

### 2. Prepare Your Data

Create different collection directory at root level, below is the directory structure:
```
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
└── Collection N/
    ├── challenge1b_input.json
    └── PDFs/
        ├── document1.pdf
        └── document2.pdf
```

### 3. Run the Container

```bash
docker run -v "$(pwd)/Collection 1":/app/Collection\ 1 document-intelligence
```
- This will output a file named `challenge1b_output_generated.json` inside the Collection 1 directory. Similarly run for others collection and you will get the desired `challenge1b_output_generated.json` for each individual collection.
