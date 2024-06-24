.PHONY: run kill build network test

NETWORK := A54A4C39-EE53-461C-8A98-CA308FE277A0
WEB_CONTAINER := web
TEST_CONTAINER := systeme_mock

run: kill build network
	docker run -d --rm --name $(WEB_CONTAINER) -p 8080:8080 --network $(NETWORK) -e SYSTEME_IO_API_KEY=123 -e SYSTEME_IO_BASE_URL=http://$(TEST_CONTAINER):8081 -v $$PWD/htdocs:/var/www/localhost/htdocs $(WEB_CONTAINER)
	docker run -d --rm --name $(TEST_CONTAINER) -p 8081:8081 --network $(NETWORK) $(TEST_CONTAINER)

kill:
	docker kill $(WEB_CONTAINER) || true
	docker kill $(TEST_CONTAINER) || true

build:
	docker build -t $(WEB_CONTAINER) .
	docker build -t $(TEST_CONTAINER) test

network:
	docker network inspect $(NETWORK) > /dev/null 2>&1 || docker network create $(NETWORK)

test: run
	while ! curl -fs -o /dev/null http://localhost:8080; do sleep 1; done
	while ! curl -fs -o /dev/null http://localhost:8081; do sleep 1; done
	docker exec -it $(TEST_CONTAINER) python3 /usr/bin/test_suite.py
