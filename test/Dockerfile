FROM python:3.12-alpine

COPY systeme-io-api-mock.py /usr/bin/systeme-io-api-mock.py
COPY test_suite.py /usr/bin/test_suite.py

RUN pip install \
    flask \
    requests

EXPOSE 8081

ENTRYPOINT ["/usr/bin/systeme-io-api-mock.py"]
