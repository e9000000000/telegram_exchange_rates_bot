FROM python:3

WORKDIR /service

RUN pip install -r requirements.txt

CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000"]