FROM python:3.6-alpine
RUN apk update && apk add --no-cache --virtual build-dependencies build-base gcc wget git
RUN pip3 install yarl==0.18.0
RUN pip3 install aiohttp==3.8.1
RUN pip3 install python-dateutil==2.6.1
RUN mkdir /app
ADD . /app
RUN cd /app && python3 setup.py install && rm -rf /app
RUN apk del build-dependencies
EXPOSE 8420
CMD ["localstripe"]