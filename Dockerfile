FROM metabrainz/python:3.6

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         build-essential \
         npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip3.6 install setuptools uwsgi

RUN mkdir -p /code/wearebeautiful.info
WORKDIR /code/wearebeautiful.info

RUN apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean -y

WORKDIR /code/wearebeautiful.info/static
RUN mkdir -p js && \
    cd js && \
    npm install && \
    npm i three

COPY . /code/wearebeautiful.info
RUN pip3.6 install -r requirements.txt

CMD uwsgi --gid=www-data --uid=www-data --http-socket :3031 \
          --vhost --module=wearebeautiful.app --callable=app --chdir=/code/wearebeautiful.info \
          --enable-threads --processes=10
