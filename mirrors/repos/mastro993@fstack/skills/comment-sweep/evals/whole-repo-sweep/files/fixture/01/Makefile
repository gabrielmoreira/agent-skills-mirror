PYTHON ?= python3
IMAGE ?= wxdata:latest

.PHONY: install test lint typecheck run-ingest report proto docker migrate clean cron-export

install:
	$(PYTHON) -m pip install -e '.[dev]'

# Run the tests
test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check wxdata tests
	$(PYTHON) -m black --check wxdata tests

#lint-old:
#	flake8 wxdata --max-line-length 100

typecheck:
	$(PYTHON) -m mypy wxdata

run-ingest:
	$(PYTHON) -m wxdata.cli ingest --day $$(date -u +%F)

report:
	mkdir -p build
	$(PYTHON) -m wxdata.cli report --day $$(date -u +%F) --out build/report.html

cron-export:
	$(PYTHON) -m wxdata.cron_export --out build/exports

proto:
	protoc --python_out=wxdata/proto --proto_path=proto proto/readings.proto

docker:
	docker build -t $(IMAGE) .

migrate:
	alembic upgrade head

clean:
	rm -rf build .pytest_cache .mypy_cache .ruff_cache
	find . -name __pycache__ -prune -exec rm -rf {} +
