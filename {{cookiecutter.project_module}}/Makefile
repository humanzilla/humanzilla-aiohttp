.PHONY: deps clean runserver start tests

deps:
	pip install -r requirements.txt
	pip install -e .

clean:
	rm -rf dist
	find . -name '*.egg' -exec rm -f {} \;
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

runserver:
	aiohttp-devtools runserver src/{{ cookiecutter.project_module }}

start:
	python src/manage.py --no-debug runserver

tests:
	py.test -vv --cov {{ cookiecutter.project_module }} --cov-report html --cov-report xml tests
