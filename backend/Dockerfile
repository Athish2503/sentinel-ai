FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV DATABASE_URL=sqlite:///./kavalar.db
ENV MODEL_NAME=llama-3.3-70b-versatile
ENV GROQ_API_KEY=your_groq_api_key_here
ENV HOST=0.0.0.0
ENV PORT=8000

# Start script: Runs baseline trainer first, then starts uvicorn
CMD python train_baseline.py && uvicorn main:app --host 0.0.0.0 --port 8000
