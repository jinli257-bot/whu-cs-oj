# 本地/内网使用；不要直接暴露到公网
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ gcc nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN mkdir -p data work

ENV PYTHONUNBUFFERED=1
EXPOSE 8765

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8765"]
