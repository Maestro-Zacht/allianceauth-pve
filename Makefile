tox_tests:
	python -m tox -v -e py311; \
	rm -rf .tox/

# Translation files
.PHONY: translations
translations:
	@echo "Creating or updating translation files"
	@django-admin makemessages -l en --ignore 'build/*' --ignore 'testauth/*' --ignore 'runtests.py'

.PHONY: compile_translations
compile_translations:
	@echo "Compiling translation files"
	@django-admin compilemessages

.PHONY: dev
dev:
	@echo "Starting development server"
	@cd frontend && npm run dev

.PHONY: clean
clean:
	rm -rf dist/
	rm -rf frontend/dist/

.PHONY: buildjs
buildjs:
	cd frontend/; npm install; npm run build; npm run buildTranslations

.PHONY: package
package: buildjs
	python -m pip install -U pip
	pip install -U build
	python -m build
