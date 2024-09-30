.PHONY: install
install: ## 🚀 Install the poetry environment and install the pre-commit hooks
	@echo "🎉 Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install
	@poetry shell

.PHONY: build-pgvector
build-pgvector:
	@eval $$(minikube docker-env) ;\
	echo "📦 Building informed-pgvector" && \
	docker build misc/images/pgvector -t gcr.io/informed/informed-pgvector:latest


.PHONY: build-pgvector-local
build-pgvector-local:
	docker build misc/images/pgvector -t gcr.io/informed/informed-pgvector:latest


.PHONY: local-db
local-db: build-pgvector-local
	docker run -d \
		-p 5432:5432 \
		-e POSTGRESQL_USERNAME=test \
		-e POSTGRESQL_PASSWORD=test \
		-e POSTGRESQL_DATABASE=test \
		-e POSTGRES_POSTGRES_PASSWORD=password \
		-e POSTGRES_INITSCRIPTS_USERNAME=postgres \
		-e POSTGRES_INITSCRIPTS_PASSWORD=password \
		--name informed-postgres \
		gcr.io/informed/informed-pgvector:latest

.PHONY: destroy-local-db
destroy-local-db:
	@docker stop informed-postgres || true
	@docker rm informed-postgres || true

.PHONY: dev.migration.create
dev.migration.create: build-pgvector-local
	@poetry run python misc/scripts/create_migration.py -m "$m"


.PHONY: code-validate ruff black prettier pyright mypy deptry validate-scenarios fstring-scanner

define run_check
	@{ \
	output=$$($(2) 2>&1); \
	exit_code=$$?; \
	total_width=70; \
	dots_width=10; \
	command_width=$$(echo -n "$(1)" | wc -c); \
	dots=$$(($$total_width - $$command_width - 7)); \
	dots=$$(($$dots > $$dots_width ? $$dots : $$dots_width)); \
	dots_string=$$(printf "%$${dots}s" | tr ' ' '.'); \
	if [ $$exit_code -eq 0 ]; then \
		echo "$(1)$${dots_string} \033[0;32mPassed\033[0m"; \
	else \
		echo "$(1)$${dots_string} \033[0;31mFailed\033[0m"; \
		echo "$$output"; \
		exit 1; \
	fi; \
}
endef

code-validate:
	@$(MAKE) -j 8 check-poetry-lock black pyright mypy deptry

check-poetry-lock:
	$(call run_check, check poetry lock file , poetry check --lock)

ruff:
	$(call run_check, ruff, poetry run ruff check .)

black:
	$(call run_check, black, poetry run black .)

pyright:
	$(call run_check, pyright, poetry run pyright)

mypy:
	$(call run_check, mypy, poetry run mypy informed)

deptry:
	$(call run_check, deptry, poetry run deptry . --extend-exclude ".*/node_modules/")


.PHONY: test-code-quality
test-code-quality: ## 🚨 Run code quality tools.
	@poetry run pre-commit run -a
