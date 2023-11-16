FROM python:3.9-slim

RUN apt-get update

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
RUN mkdir app/validation
WORKDIR /app

ADD . /app/validation


RUN useradd app
RUN chown -R app:app /app
USER app


ENTRYPOINT [ "python", "-m", "validation.server" ]
