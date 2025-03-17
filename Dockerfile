FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create vector DB directory
RUN mkdir -p ./data/vector_store

# Run the application
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:5000", "--workers", "4"]


