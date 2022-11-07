FROM python:3.11-rc-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/foospoll

# psycopg2 deps
RUN apk update && apk add build-base libpq postgresql-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . .

CMD ["python3", "foospollbot/bot.py"]