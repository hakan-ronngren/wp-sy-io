.PHONY: run kill build network test list-mock-requests browse staging clean

NETWORK := test-a54a4c39
WEB_CONTAINER := web
TEST_CONTAINER := systeme_mock
PROD_WEB_CONTAINER := web-prod

# Run the web container and the test container
run: build network kill
	docker run -d --rm --name $(WEB_CONTAINER) -p 8080:8080 --network $(NETWORK) -e API_KEY=$(shell printf '%.0s0' {1..64}) -e API_BASE_URL=http://$(TEST_CONTAINER):8081 -v $$PWD/htdocs:/var/www/localhost/htdocs $(WEB_CONTAINER)
	docker run -d --rm --name $(TEST_CONTAINER) -p 8081:8081 --network $(NETWORK) $(TEST_CONTAINER)

# Run a separate web container that targets the production API
run-prod: build kill
	test -n "$$SYSTEME_IO_API_KEY" || (echo "SYSTEME_IO_API_KEY is not set" && exit 1)
	docker run -d --rm --name $(PROD_WEB_CONTAINER) -p 8888:8080 -e API_KEY=$$SYSTEME_IO_API_KEY -e API_BASE_URL=https://api.systeme.io -v $$PWD/htdocs:/var/www/localhost/htdocs $(WEB_CONTAINER)

kill:
	docker ps --format "{{.Names}}" | grep -E "$(WEB_CONTAINER)|$(TEST_CONTAINER)|$(PROD_WEB_CONTAINER)" | while read -r c; do docker kill $$c; done

build:
	docker build -t $(WEB_CONTAINER) .
	docker build -t $(TEST_CONTAINER) test

network:
	docker network inspect $(NETWORK) > /dev/null 2>&1 || docker network create $(NETWORK)

# To run one single test, use the following command:
# make test one_test=<class_name>.<test_name>
test: run
	while ! curl -fs -o /dev/null http://localhost:8080; do sleep 1; done
	while ! curl -fs -o /dev/null http://localhost:8081; do sleep 1; done
	docker exec -it -w /opt $(TEST_CONTAINER) python3 test/test_all.py $(one_test) | sed 's|File "/opt/|File "|'

list-mock-requests:
	docker exec -it systeme_mock cat /var/log/requests.txt

browse: run
	open http://localhost:8080/sample-form.html

staging: test
	mkdir staging 2> /dev/null && cp templates/systeme-io-config.php staging/ || true
	cp htdocs/add-systeme-io-contact.php staging/

clean: kill
	docker rmi $(WEB_CONTAINER) || true
	docker rmi $(TEST_CONTAINER) || true
	docker network rm $(NETWORK) || true
	rm -rf test/*.pyc test/__pycache__ staging
