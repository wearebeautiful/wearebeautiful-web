FROM nginx:1.17.8

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
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install setuptools

RUN mkdir -p /code/wearebeautiful.info
WORKDIR /code/wearebeautiful.info
COPY requirements.txt /code/wearebeautiful.info
RUN pip3 install -r requirements.txt

RUN apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean -y

WORKDIR /code/wearebeautiful.info
COPY . /code/wearebeautiful.info

WORKDIR /code/wearebeautiful.info/static
RUN rm -rf js && \
    mkdir js && \
    cd js && \
    npm install && \
    npm i three@0.115.0 && \
    npm i bootstrap@4.4.1 \
    npm i sass@1.26.3

WORKDIR /code/wearebeautiful.info
ENV FLASK_APP=wearebeautiful.app
ENV FLASK_ENV=production
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN flask digest compile

#CMD uwsgi --ini /code/wearebeautiful.info/admin/uwsgi/uwsgi.ini
