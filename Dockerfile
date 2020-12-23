FROM puckel/docker-airflow:1.10.4

USER root

RUN curl -sSL https://get.docker.com/ | sh

RUN pip install --upgrade pip && \
    pip install docker==4.1.0