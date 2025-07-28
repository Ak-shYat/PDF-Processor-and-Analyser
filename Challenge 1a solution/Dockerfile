FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Set entrypoint to main.py
ENTRYPOINT ["python", "main.py"]
