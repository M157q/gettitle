install:
	poetry install

test:
	poetry run flake8 . --ignore=E121,E123,E126,E226,E24,E704,W503,W504,E501
	poetry run python -m unittest
