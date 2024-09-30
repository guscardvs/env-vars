.PHONY: format
format:
	@ruff check --fix config tests
	@ruff format config tests

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