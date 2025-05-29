# Stage 1: Builder
FROM python:3.10-slim AS builder

WORKDIR /app

# Install system dependencies required for Python packages (e.g., for cryptography, Pillow, etc.)
# Add any specific system packages your Python libraries might need.
# Example: libpq-dev for psycopg2, build-essential for some wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
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
ENV PYTHONPATH /app

# Install only runtime system dependencies (if any, e.g., libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and executables from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set PATH to include Python executables (applies to subsequent USER)
ENV PATH="/usr/local/bin:$PATH"

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
ARG BUILD_DATE
# Copy the rest of the application code
COPY . .

# Change ownership of the app directory to appuser
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Default command for FastAPI application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]