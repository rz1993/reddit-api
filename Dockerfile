FROM python:3.6-alpine

RUN adduser -D reddit

WORKDIR /home/reddit

COPY requirements requirements

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev \
  && apk add --no-cache openssl-dev libffi-dev \
  && python3 -m pip install -r requirements/development.txt

COPY reddit reddit
COPY migrations migrations
#COPY scripts scripts
COPY tests tests
COPY app.py config.py run.sh ./

RUN chmod +x run.sh
RUN chown -R reddit:reddit ./

EXPOSE 5000
ENTRYPOINT ["./run.sh"]
