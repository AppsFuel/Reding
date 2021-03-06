install-dev-requirements:
	pip install -q -e .

install-test-requirements:
	pip install -q -r test_requirements.txt

test-python:
	@echo "Running Python tests"
	python setup.py test || exit 1
	@echo ""

develop: install-dev-requirements install-test-requirements

test: develop test-python

publish:
	python setup.py sdist upload

clean:
	rm -rf __pycache__
	rm -rf dist
	rm -rf *.egg-info

.PHONY: publish clean
