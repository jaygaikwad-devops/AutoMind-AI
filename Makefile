# AutoMind AI — One-Command Makefile
.PHONY: up down logs clean setup help

up: ## Build and start all services with Docker Compose
	./setup.sh up

down: ## Stop all services
	./setup.sh down

logs: ## Follow all service logs
	./setup.sh logs

clean: ## Stop services and remove all data volumes
	./setup.sh clean

setup: ## Alias for 'up' — full one-command setup
	./setup.sh up

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
