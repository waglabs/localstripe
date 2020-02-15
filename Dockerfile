FROM python:3
RUN mkdir /app
ADD . /app
RUN cd /app && python3 setup.py install && rm -rf /app
EXPOSE 8420
CMD ["localstripe"]
