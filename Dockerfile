FROM python:3.10-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
COPY ./backend /code/backend

# Create data directory and set permissions
RUN mkdir -p /code/backend/data && \
    chmod 777 /code/backend/data

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 7860

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /code

# Switch to non-root user
USER appuser

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"] 