
FROM python:3.11-slim
 
WORKDIR /app
 
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
 
# Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy seluruh backend
COPY . .
 
# Buat folder yang diperlukan
RUN mkdir -p uploads chroma_db
 
# Expose port
EXPOSE 8080
 
# Jalankan app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]