FROM nginx:1.19.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         build-essential \
         npm \
         nginx \
         python3 \
         python3-dev \
         python3-pip \
         uwsgi \
         uwsgi-plugin-python3 \
         libpcre3-dev \
         libz-dev \
         zip \
    && rm -rf /var/lib/apt/lists/*
RUN curl https://www.npmjs.com/install.sh | sh

RUN pip3 install setuptools

RUN mkdir -p /code/wearebeautiful.info && mkdir /kits
WORKDIR /code/wearebeautiful.info
COPY requirements.txt /code/wearebeautiful.info
RUN pip3 install -r requirements.txt

RUN apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean -y

WORKDIR /code/wearebeautiful.info
COPY . /code/wearebeautiful.info

WORKDIR /code/wearebeautiful.info/static
RUN rm -rf js gcss && \
    mkdir js gcss && \
    cd js && \
    npm install && \
    npm i -g sass@1.26.3 && \
    npm i bootstrap@4.4.1 jquery@3.5.0 popper.js@^1.16.0
RUN sass --load-path=./js/node_modules/bootstrap/scss \
         --load-path=./ scss/custom.scss \
         /code/wearebeautiful.info/static/gcss/bootstrap.css

WORKDIR /code/wearebeautiful.info
ENV FLASK_APP=wearebeautiful.app
ENV FLASK_ENV=production
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN flask digest compile
