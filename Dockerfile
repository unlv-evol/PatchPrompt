FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements-lock.txt requirements.txt ./
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements-lock.txt

COPY . .

CMD ["bash", "-lc", "make reproduce && make verify"]
