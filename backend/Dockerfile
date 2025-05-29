# Stage 1: Builder
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies required for Python packages (e.g., for cryptography, Pillow, etc.)
# Add any specific system packages your Python libraries might need.
# Example: libpq-dev for psycopg2, build-essential for some wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    # libpq-dev \ # Example: if using PostgreSQL
    # libjpeg-dev zlib1g-dev \ # Example: if using Pillow
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3.10-slim AS runner

WORKDIR /app

# Prevents Python from writing pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install only runtime system dependencies (if any, e.g., libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # libpq5 \ # Example: if using PostgreSQL
    # libjpeg62-turbo \ # Example: if using Pillow
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Set PATH for non-root user to include Python executables
ENV PATH="/usr/local/bin:$PATH"

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy the rest of the application code
COPY . .

EXPOSE 8000

# Default command for FastAPI application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]