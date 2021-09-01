FROM python:3 AS base

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /service

FROM base AS debug
RUN pip install ptvsd
CMD python -m ptvsd --host 0.0.0.0 --port 5678 --wait --multiprocess .

FROM base AS prod
CMD python .
