.PHONY: run tests dist

deps:
	python setup.py install

clean:
	rm -rf dist
	find . -name '*.egg' -exec rm -f {} \;
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

dist:
	python setup.py sdist

run:
	{{ cookiecutter.project_module }} run --host=$(host)

tests:
	py.test -vv --cov {{ cookiecutter.project_module }} --cov-report html --cov-report xml tests
