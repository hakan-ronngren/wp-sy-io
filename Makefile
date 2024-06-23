.PHONY: run kill build add-test-user network test

NETWORK := A54A4C39-EE53-461C-8A98-CA308FE277A0
PHP_CONTAINER := php
TEST_CONTAINER := systeme_mock

run: kill build network
	docker run -d --rm --name $(PHP_CONTAINER) -p 8080:8080 --network $(NETWORK) -e SYSTEME_IO_API_KEY=123 -e SYSTEME_IO_BASE_URL=http://$(TEST_CONTAINER):8081 -v $$PWD/htdocs:/var/www/localhost/htdocs $(PHP_CONTAINER)
	docker run -d --rm --name $(TEST_CONTAINER) -p 8081:8081 --network $(NETWORK) $(TEST_CONTAINER)

kill:
	docker kill $(PHP_CONTAINER) || true
	docker kill $(TEST_CONTAINER) || true

build:
	docker build -t $(PHP_CONTAINER) .
	docker build -t $(TEST_CONTAINER) test

add-test-user:
	curl --request POST --url http://localhost:8080/add-subscriber.php --data "email=test-$$(date +%s)@haliro.se"
	: curl --request POST --url http://localhost:8080/add-subscriber.php --data "email=test-@haliro.se"

network:
	docker network inspect $(NETWORK) > /dev/null 2>&1 || docker network create $(NETWORK)

test: run
	# Docker exec into the test container and run test_suite.py
	docker exec -it $(TEST_CONTAINER) python3 /usr/bin/test_suite.py
