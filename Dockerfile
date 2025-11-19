# FROM python:3.11-slim
# ENV PYTHONUNBUFFERED=1
# WORKDIR /code
# COPY requirements.txt /code/
# RUN /usr/local/bin/python -m pip install --upgrade pip
# RUN pip install -r requirements.txt
# COPY . /code/

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY requirements.txt /code/

# 🔧 instalar gcc y herramientas necesarias
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       python3-dev \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code/



