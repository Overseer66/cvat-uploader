FROM python:3.10.14

RUN apt-get upgrade
RUN apt-get update
RUN apt-get install -y git wget

WORKDIR /workspace/dev

COPY . .

RUN pip install pip --upgrade
RUN pip install -r requirements.txt
