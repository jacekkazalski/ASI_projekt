FROM python:3.11-slim

WORKDIR /app

COPY api/api_requirements.txt .

RUN pip install -r api_requirements.txt

COPY api /app

COPY models /app/models

EXPOSE 5000

CMD ["python", "api.py"]