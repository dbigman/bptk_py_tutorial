.PHONY: compose_up compose_down lint run_toy debrief test

compose_up:
	docker-compose up -d --build

compose_down:
	docker-compose down

lint:
	# Type checks and style checks (adjust to your toolchain)
	mypy .
	flake8 .
	# Validate OpenAPI (install swagger-cli separately)
	# swagger-cli validate api/openapi.yaml

run_toy:
	# Run a quick toy run (expects local env populated from .env)
	python -m main

debrief:
	# Placeholder target to produce a debrief artifact (pipeline to be implemented)
	@echo "Render debrief (placeholder)"

test:
	pytest -q