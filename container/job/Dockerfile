FROM python:3.8-slim

RUN pip install \
    psycopg2-binary==2.9.7


WORKDIR /opt/job

COPY ../../job /opt/job

CMD [ "python" "./main/main.py"]