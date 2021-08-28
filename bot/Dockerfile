FROM python:3

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /service

CMD ["python", "."]
