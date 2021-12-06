FROM ubuntu:20.04

WORKDIR /app
COPY . /app

RUN apt-get update -y
RUN apt-get install -y locales
RUN locale-gen "es_ES.UTF-8"
RUN update-locale LC_ALL="es_ES.UTF-8"
RUN dpkg-reconfigure locales

RUN apt install tzdata -y
ENV TZ="America/Santiago"

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN pip3 install -r requirements.txt

CMD [ "python3", "pipeline.py" ]