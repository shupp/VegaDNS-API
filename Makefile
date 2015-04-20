# You'll need to source venv/bin/activate before running this file

default: check test

# Only check code we've written
check:
	pep8 vegadns tests

# Test everything in the tests directory
test:
	nosetests tests
