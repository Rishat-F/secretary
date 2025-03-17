.PHONY: secretary_up
secretary_up:
	docker compose up -d --build

.PHONY: secretary_down
secretary_down:
	docker compose down

.PHONY: lint
lint:
	ruff check
