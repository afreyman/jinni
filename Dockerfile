FROM alpine
RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*
RUN mkdir /build
RUN mkdir /root/.aws
ADD . /build
WORKDIR build/
RUN /usr/bin/python setup.py install
ENTRYPOINT ["/usr/bin/jinni"]