FROM python:3

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /service


CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000"]
