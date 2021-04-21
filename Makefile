.PHONY: clean install dist

clean:
	pip uninstall chemconda -y
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

install:
	python setup.py install

dist:
	rm -rf dist/*
	python setup.py sdist