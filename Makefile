ifeq ("$(UP_ARGS)","")
        UP_ARGS="-d"
endif

ifeq ("$(COMPOSE_PROJECT_NAME_SUFFIX)","")
        # Local use case
        COMPOSE_PROJECT_NAME=vegadnsapi
        COMPOSE_FILE=docker-compose.yml
else
        # CI/CD use case
        COMPOSE_PROJECT_NAME=vegadnsapiintegration$(COMPOSE_PROJECT_NAME_SUFFIX)
        COMPOSE_FILE=docker-compose-$(COMPOSE_PROJECT_NAME).yml
endif

# You'll need to source venv/bin/activate before running this file
.PHONY: coverage

default: check test

# Only check code we've written
check:
	pep8 vegadns tests run.py
up:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker-compose up $(UP_ARGS)
down:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker-compose down
logs:
	# To follow logs: LOGS_ARGS="-f" make logs
	# To follow logs for a service: LOGS_ARGS="-f <service>" make logs
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) docker-compose logs $(LOGS_ARGS)
test-docker: up
	docker-compose -f docker-compose-test.yml run --rm api_unittest
# Test everything in the tests directory
test:
	nosetests tests
coverage:
	nosetests --with-coverage --cover-package vegadns tests
coverage-html: clean-coverage
	nosetests --with-coverage --cover-html --cover-html-dir coverage --cover-package vegadns tests
clean: clean-coverage
clean-coverage:
	rm -rf coverage .coverage
clean-python:
	find vegadns tests -name "*.pyc" -exec rm {} \;
test-integration:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) ./run_integration_tests.sh
