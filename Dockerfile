# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvicorn

# Copy dependency files for Next.js
COPY nextjs-app/package.json nextjs-app/package-lock.json ./nextjs-app/

# Install Node.js dependencies
WORKDIR /app/nextjs-app
RUN npm ci

# Copy the rest of the application
WORKDIR /app
COPY . .

# Build Next.js application
WORKDIR /app/nextjs-app
RUN npm run build
WORKDIR /app

# Expose ports
EXPOSE 8000 3000

# Start command (using unified launcher)
CMD ["python", "unified_launcher.py", "--mode", "fullstack", "--production", "--non-interactive"]
