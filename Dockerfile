FROM python:3

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "."]
