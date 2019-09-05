FROM python:3-alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip3 install --user --force-reinstall localstripe
CMD ["localstripe"]
