# Development Environment Setup
.PHONY: install setup-local setup-windows-local
install: ## 🚀 Install the poetry environment and install the pre-commit hooks
	@echo "🎉 Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install
	@poetry shell

setup-local: install-local-domain add-helm-repos

# Database Management
.PHONY: build-pgvector build-pgvector-local local-db destroy-local-db


build-pgvector-local:
	docker build misc/images/pgvector -t gcr.io/informed/informed-pgvector:latest

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

destroy-local-db:
	@docker stop informed-postgres || true
	@docker rm informed-postgres || true

# Migration
.PHONY: dev.migration.create
dev.migration.create: build-pgvector-local
	@poetry run python misc/scripts/create_migration.py -m "$m"

# Code Quality and Validation
.PHONY: code-validate check ruff black pyright mypy deptry
code-validate:
	@$(MAKE) -j 8 check-poetry-lock black pyright mypy deptry

check: ## 🚨 Run code quality tools.
	@poetry run pre-commit run -a

# ... (keep the individual check definitions like ruff, black, etc.)

# Docker Image Building and Pushing
.PHONY: build-ui build-core build-pgvector push-images
GCP_PROJECT_ID := informed-ai-prod

build-ui:
	@echo "📦 Building informed-ui for AMD64"
	docker buildx create --use
	docker buildx build --platform linux/amd64 \
		-t gcr.io/$(GCP_PROJECT_ID)/informed-ui:latest \
		--push frontend

build-core:
	@echo "📦 Building informed-core for AMD64"
	docker buildx create --use
	docker buildx build --platform linux/amd64 \
		-t gcr.io/$(GCP_PROJECT_ID)/informed-core:latest \
		--build-arg=APP_VERSION="latest" \
		--push .

build-pgvector:
	@echo "📦 Building informed-pgvector for AMD64"
	docker buildx create --use
	docker buildx build --platform linux/amd64 \
		-t gcr.io/$(GCP_PROJECT_ID)/informed-pgvector:latest \
		--push misc/images/pgvector

# Minikube and Kubernetes
.PHONY: ensure-minikube run-local
ensure-minikube:
	@if [ "$$(kubectl config current-context)" != "minikube" ]; then \
    	  echo "Error: The current kubectl context is not set to 'minikube'."; \
    	  exit 1; \
	fi

run-local: ensure-minikube build-ui build-core build-pgvector
	IMAGE_TAG=latest env=local $(MAKE) install-helm-chart-from-local-chart
	@echo "Tunnelling minikube..."
	@minikube tunnel

# Helm Chart Installation
.PHONY: install-helm-chart-from-local-chart install-helm-chart add-helm-repos
install-helm-chart-from-local-chart: .requires_image_tag
	@set -a && . ./.env && \
	envsubst < charts/informed/values.template.yaml > charts/informed/values.yaml && \
	$(MAKE) install-helm-chart CHART="charts/informed" version="0.1.0" extra="-f charts/informed/values.yaml -f charts/$(env).values.yaml $(extra)" && \
	rm charts/informed/values.yaml
	@echo "✅ Helm chart installed for $(env) environment."

install-helm-chart: .requires_version .requires_env
	@set -a && . ./.env && \
	envsubst < charts/$(env).values.yaml > charts/values.yaml && \
	helm upgrade \
		informed \
		$(CHART) \
		--install \
		-n informed \
		--create-namespace \
		--version $(version) $(extra) \
		-f charts/values.yaml && \
	rm charts/values.yaml
	@echo "✅ Installed."

add-helm-repos:
	@helm repo add jetstack https://charts.jetstack.io || True && \
    helm repo add traefik https://helm.traefik.io/traefik || True && \
    helm repo add bitnami https://charts.bitnami.com/bitnami || True && \
    helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts || True && \
    helm dependency build charts/informed

# Certificate and Domain Setup
.PHONY: install-self-signed-cert install-local-domain install-self-signed-cert-windows install-local-domain-windows
install-self-signed-cert:
	sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "charts/informed/localCerts/informedCA.crt"

install-local-domain: install-self-signed-cert
	echo "127.0.0.1	local.app.informed.com" | sudo tee -a /etc/hosts

install-self-signed-cert-windows:
	@echo "Installing self-signed certificate on Windows..."
	@powershell -Command "Import-Certificate -FilePath 'charts\informed\localCerts\informedCA.crt' -CertStoreLocation Cert:\LocalMachine\Root"

install-local-domain-windows: install-self-signed-cert-windows
	@echo "Adding local domain to hosts file on Windows..."
	@powershell -Command "Add-Content -Path 'C:\Windows\System32\drivers\etc\hosts' -Value '127.0.0.1 local.app.informed.com' -Force"

# Utility Functions
.PHONY: .requires_env .requires_image_tag .requires_version
.requires_env:
ifndef env
	$(error env is required)
endif

.requires_image_tag:
ifndef IMAGE_TAG
	$(error IMAGE_TAG is required)
endif

.requires_version:
ifndef version
	$(error version is required)
endif

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

# GCP Deployment
.PHONY: gcp-deploy gcp-build-push

gcp-build-push: build-ui build-core build-pgvector
	@echo "✅ Images built and pushed to Google Container Registry"

gcp-deploy:
	@echo "🚀 Deploying to GCP"
	IMAGE_TAG=latest env=prod $(MAKE) install-helm-chart-from-local-chart CHART="charts/informed" version="0.1.0" extra="-f charts/informed/values.yaml -f charts/prod.values.yaml"
