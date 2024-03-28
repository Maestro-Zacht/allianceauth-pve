tox_tests:
	python -m tox -v -e py311; \
	rm -rf .tox/