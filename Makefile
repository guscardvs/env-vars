format:
	@black src tests
	@isort src tests
	@autoflake --remove-all-unused-imports --remove-unused-variables --recursive --in-place src tests
