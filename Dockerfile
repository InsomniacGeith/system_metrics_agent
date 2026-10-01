FROM python:3.12-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y procps

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS agent

CMD ["python", "-m", "app.agent"]