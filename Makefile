# You'll need to source venv/bin/activate before running this file
.PHONY: coverage

default: check test

# Only check code we've written
check:
	pep8 vegadns tests run.py

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
