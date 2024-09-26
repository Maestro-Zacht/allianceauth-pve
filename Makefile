tox_tests:
	python -m tox -v -e py311; \
	rm -rf .tox/

# Translation files
.PHONY: translations
translations:
	@echo "Creating or updating translation files"
	@django-admin makemessages -l en --ignore 'build/*'

.PHONY: compile_translations
compile_translations:
	@echo "Compiling translation files"
	@django-admin compilemessages
