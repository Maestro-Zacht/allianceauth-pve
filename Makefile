.PHONY: tox_tests
tox_tests:
	uvx --with tox-uv --with tox-gh-actions tox -v -e py312; \
	status=$$?; \
	rm -rf .tox/; \
	exit $$status

# Translation files
.PHONY: translations
translations:
	@echo "Creating or updating translation files"
	@uv run django-admin makemessages -l en -l it_IT --ignore 'build/*' --ignore 'testauth/*' --ignore 'runtests.py'

.PHONY: compile_translations
compile_translations:
	@echo "Compiling translation files"
	@uv run django-admin compilemessages

.PHONY: dev
dev:
	@echo "Starting development server"
	@cd frontend && pnpm dev

.PHONY: clean
clean:
	rm -rf dist/
	rm -rf frontend/dist/

.PHONY: buildjs
buildjs:
	cd frontend/ && pnpm install --frozen-lockfile && pnpm run build && ./copy-langs.sh

.PHONY: package
package: buildjs
	uv build --no-sources --out-dir dist/
