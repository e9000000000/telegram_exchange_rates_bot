FROM python:3 as base

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /service

FROM base as debug
RUN pip install ptvsd
CMD python -m ptvsd --host 0.0.0.0 --port 5678 --wait --multiprocess -m \
    uvicorn service.app:app --host 0.0.0.0 --port 8000 --reload

FROM base as prod
CMD uvicorn service.app:app --host 0.0.0.0 --port 8000 --reload
