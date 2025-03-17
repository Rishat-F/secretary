.PHONY: secretary_up
secretary_up:
	docker compose -f code/compose.yml up -d --build

.PHONY: secretary_down
secretary_down:
	docker compose -f code/compose.yml down

.PHONY: lint
lint:
	ruff check code
