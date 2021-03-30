FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update; apt-get --assume-yes install binutils libproj-dev gdal-bin gettext
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install --no-cache-dir -r /code/requirements.txt

