FROM python:3-alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN python3 setup.py install
CMD ["localstripe"]
