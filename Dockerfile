# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files only (sem banco de dados)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Usar start.sh para migrations + servidor
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]