FROM python:3.7-slim

RUN pip install \
    psycopg2-binary==2.9.7 \
    faker==13.3.2 


WORKDIR /opt/datagen

COPY ../../datagen /opt/datagen

CMD [ "python" "./gen_user_payment_data.py"]