PATH := .venv/bin:$(PATH)

.PHONY: deps
default:
	pip install -r requirements.txt
	pip install -e .

.PHONY: clean
clean:
	rm -rf dist
	find . -name '*.egg' -exec rm -f {} \;
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

.PHONY: runserver
runserver:
	aiohttp-devtools runserver src/{{ cookiecutter.project_module }}

.PHONY: start
start:
	python src/manage.py --no-debug runserver

.PHONY: tests
tests:
	py.test -vv \
		--cov {{ cookiecutter.project_module }} \
		--cov-report html \
		--cov-report xml tests

.PHONY: isort
isort:
	isort -rc src/{{ cookiecutter.project_module }}

.PHONY: linter
linter:
	flake8 src/{{ cookiecutter.project_module }}
