FROM python:3.12-alpine

COPY server.py /usr/bin/server.py
COPY test_suite.py /usr/bin/test_suite.py

RUN pip install \
    flask \
    requests

EXPOSE 8081

ENTRYPOINT ["/usr/bin/server.py"]
