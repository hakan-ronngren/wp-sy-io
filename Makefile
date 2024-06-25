.PHONY: run kill build network test browse staging clean

NETWORK := test-a54a4c39
WEB_CONTAINER := web
TEST_CONTAINER := systeme_mock

run: build network kill
	docker run -d --rm --name $(WEB_CONTAINER) -p 8080:8080 --network $(NETWORK) -e API_KEY=$(shell printf '%.0s0' {1..64}) -e API_BASE_URL=http://$(TEST_CONTAINER):8081 -v $$PWD/htdocs:/var/www/localhost/htdocs $(WEB_CONTAINER)
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
	docker exec -it -w /opt $(TEST_CONTAINER) python3 test/test_api_mock.py | sed 's|File "/opt/|File "|'
	docker exec -it -w /opt $(TEST_CONTAINER) python3 test/test_suite.py | sed 's|File "/opt/|File "|'

browse: run
	open http://localhost:8080/form.html

staging: test
	mkdir staging 2> /dev/null && cp templates/production-config.php staging/ || true
	cp htdocs/add-subscriber.php staging/

clean: kill
	docker rmi $(WEB_CONTAINER) || true
	docker rmi $(TEST_CONTAINER) || true
	docker network rm $(NETWORK) || true
	rm -rf test/*.pyc test/__pycache__ || true
