.PHONY: format
format:
	@isort config tests
	@black config tests
	@docformatter --in-place `find ./config -name '*.py' -type f`
	@autoflake --remove-all-unused-imports --remove-unused-variables --recursive --in-place config tests

.PHONY: lint
lint:
	@flake8 config
	@mypy config

.PHONY: test
test:
	@pytest tests

.PHONY: clean
clean:
	rm -rf ./dist

.PHONY: build
build: clean
	@python -m build

.PHONY: upload
upload:
	@twine upload dist/*

.PHONY: build-upload
build-upload: build upload
	@echo ""