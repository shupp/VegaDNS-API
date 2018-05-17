ifeq ("$(UP_ARGS)","")
        UP_ARGS="-d"
endif

ifeq ("$(COMPOSE_PROJECT_NAME_SUFFIX)","")
        # Local use case
        COMPOSE_PROJECT_NAME=vegadns-api
else
        # CI/CD use case
        COMPOSE_PROJECT_NAME=vegadnsapiintegration$(COMPOSE_PROJECT_NAME_SUFFIX)
endif

# You'll need to source venv/bin/activate before running this file
.PHONY: coverage

default: pull build-api up test-integration down


# Docker compose targets
pull:
	docker-compose -f docker-compose/network.yml \
		-f docker-compose/base.yml \
		-f docker-compose/split.yml pull
	docker-compose -f docker-compose/network.yml \
		-f docker-compose/base.yml \
		-f docker-compose/apiui.yml pull api
	docker-compose -f docker-compose/network.yml \
		-f docker-compose/test-integration.yml pull

# vegadns/api and vegadns/ui (split) image targets
up:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/base-ports.yml \
			-f docker-compose/split.yml \
			-f docker-compose/split-ports.yml \
			up $(UP_ARGS)
down:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/base-ports.yml \
			-f docker-compose/split.yml \
			-f docker-compose/split-ports.yml \
			down
up-no-ports:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/split.yml \
			up $(UP_ARGS)
down-no-ports:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/split.yml \
			down
logs:
	# To follow logs: LOGS_ARGS="-f" make logs
	# To follow logs for a service: LOGS_ARGS="-f <service>" make logs
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/split.yml \
			logs $(LOGS_ARGS)


# vegadns/apiui image targets
up-apiui:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/base-ports.yml \
			-f docker-compose/apiui.yml \
			-f docker-compose/apiui-ports.yml \
			up $(UP_ARGS)
down-apiui:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/base-ports.yml \
			-f docker-compose/apiui.yml \
			-f docker-compose/apiui-ports.yml \
			down
up-apiui-no-ports:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/apiui.yml \
			up $(UP_ARGS)
down-apiui-no-ports:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/apiui.yml \
			down
logs-apiui:
	# To follow logs: LOGS_ARGS="-f" make logs
	# To follow logs for a service: LOGS_ARGS="-f <service>" make logs-apiui
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) \
		 docker-compose -f docker-compose/network.yml \
			-f docker-compose/base.yml \
			-f docker-compose/apiui.yml \
			logs $(LOGS_ARGS)
dev-db:
	mysql -u vegadns -psecret -h 127.0.0.1 vegadns


# Tests, cleaning targets
venv:
	(virtualenv venv \
		&& source venv/bin/activate \
		&& pip install -r requirements.txt)
check: venv
	# Only check code we've written
	source venv/bin/activate && \
		pep8 vegadns tests run.py
test-integration:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) ./run_integration_tests.sh
test-integration-apiui:
	COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) API_URL=http://localhost HOST=http://api:80 ./run_integration_tests.sh
test-docker:
	docker-compose -f docker-compose/test.yml run --rm api_unittest
test: venv check
	source venv/bin/activate && \
		nosetests tests
coverage: venv clean-coverage
	source venv/bin/activate && \
		nosetests --with-coverage --cover-package vegadns tests
coverage-html: venv clean-coverage
	source venv/bin/activate && \
		nosetests --with-coverage --cover-html --cover-html-dir coverage --cover-package vegadns tests
	open coverage/index.html
clean: clean-python clean-coverage clean-venv
clean-coverage:
	rm -rf coverage .coverage
clean-python:
	find vegadns tests run.pyc -name "*.pyc" -exec rm {} \;
clean-venv:
	rm -rf venv


# Build targets
build-api:
	docker build --no-cache -t vegadns/api .
build-apiui:
	docker build --no-cache -f docker/Dockerfile.apiui -t vegadns/apiui .
