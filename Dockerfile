FROM python:3.11-slim
WORKDIR /app

# Install Python deps (if requirements.txt exists)
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt || true
# Ensure minimal runtime deps for Phase 0
RUN python -m pip install --no-cache-dir uvicorn fastapi pydantic

# Copy app
COPY . .

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]