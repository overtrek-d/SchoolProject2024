FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r server/requirements.py

CMD ["python", "server/main.py"]
