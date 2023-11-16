FROM python:3.9-slim

RUN apt-get update
RUN apt-get install r-base -y


COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
RUN mkdir app/autoregressive
WORKDIR /app

ADD . /app/autoregressive


RUN useradd app
RUN chown -R app:app /app
USER app


ENTRYPOINT [ "python", "-m", "autoregressive.server" ]
