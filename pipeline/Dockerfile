FROM python:3.8

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

RUN apt-get install -y locales
RUN locale-gen "es_ES.UTF-8"
RUN update-locale LC_ALL="es_ES.UTF-8"

CMD [ "python", "pipeline.py" ]