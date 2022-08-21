format:
	@black config tests
	@isort -ir config tests
	@autoflake --remove-all-unused-imports --remove-unused-variables --recursive --in-place config tests

lint:
	@flake8 config
	@mypy config

test:
	@pytest tests