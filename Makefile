.PHONY: all tests clean

install-dev:
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type pre-push
	make build-dev

build-dev:
	pip install --no-cache-dir -U pip pipenv
	pipenv install --dev

tests:
	pipenv run python -m pytest -v tests --cov=./mondu_data_science_lab --cov-branch

slow-tests:
	pipenv run python -m pytest -v tests --cov=./mondu_data_science_lab --cov-branch -m slow --run-slow

format:
	pipenv run isort .
	pipenv run black .

check:
	pipenv run isort . -c
	pipenv run black . --check
	pipenv run bandit -r mondu_website_scrapper -c "pyproject.toml"
	pipenv run flake8 mondu_website_scrapper
	pipenv run pylint mondu_website_scrapper