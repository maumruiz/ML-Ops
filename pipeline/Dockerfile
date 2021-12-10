FROM python:3.8

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pip install wandb
RUN pip install seaborn

RUN wandb login 88d0d865251eba2f98061ab1ffc9fa1af0dfe218

CMD [ "python", "pipeline.py" ]