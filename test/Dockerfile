FROM python:3.12-alpine

RUN mkdir /opt/test
COPY api_mock.py /usr/bin/api_mock.py
COPY test_*.py /opt/test
RUN chmod +x /usr/bin/api_mock.py /opt/test/test_*.py

RUN pip install \
    flask \
    requests

EXPOSE 8081

ENTRYPOINT ["/usr/bin/api_mock.py"]
