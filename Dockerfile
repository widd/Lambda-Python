FROM python:2

RUN mkdir -p /app/uploads

WORKDIR /app

RUN apt-get update
RUN apt-get install -q -y curl
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install -q -y \
    openjdk-7-jre-headless \
    nodejs \
    ruby-sass \
    libjpeg-dev
RUN npm install -g coffee-script

COPY dev.cfg ./app.cfg
COPY lmda ./lmda
COPY thumnail_create ./thumnail_create
COPY timeout.py .
COPY requirements.txt .
COPY start.sh /start.sh

RUN pip install -r requirements.txt
RUN pip install gunicorn

ENV LAMBDA_CONFIG /app/app.cfg

RUN chmod +x /start.sh
CMD ["/start.sh"]