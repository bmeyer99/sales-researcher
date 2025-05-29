FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# System dependencies can be installed here if needed by Python packages
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# If using Poetry:
# COPY pyproject.toml poetry.lock* ./
# RUN pip install poetry
# RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

COPY . .

EXPOSE 8000
# Assumes your FastAPI app instance is in 'main.py' and named 'app'.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]