# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=chat-history
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password

# Command to run the application
CMD ["streamlit", "run", "app/main.py", "--server.address", "0.0.0.0"] 