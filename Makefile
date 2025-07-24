TOOL := poetry

all: setup_poetry


setup_poetry: .mk_poetry


.mk_poetry: poetry.lock
	poetry install
	touch .mk_poetry

update: setup_poetry
	poetry update

clean:
	poetry env remove --all
	rm -rf .mk_poetry* dist

check: setup_poetry flake8 pylint mypy

pylint flake8 mypy: setup_poetry
	poetry run $@ osia tests

black-check: setup_poetry
	poetry run black --check osia

tests: setup_poetry
	poetry run pytest ${flags} -n 4 -v tests

dist: setup_poetry
	poetry build

release: dist
	poetry publish

.PHONY: update clean all check black-check pylint flake8 mypy tests
