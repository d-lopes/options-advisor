FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY src/ ./src

CMD python ./src/run.py