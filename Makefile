.PHONY: start sync run format lint ingest ingest-doc query test test-all \
        solr-up solr-down solr-wait solr-setup pipeline e2e clean

sync:
	uv sync --dev

start: sync
	uv run python src/main.py ingest

run:
	uv run python src/main.py

format:
	uv run ruff format src/ tests/

lint:
	uv run ruff check src/ tests/

SOLR_CONTAINER = solr-hybrid-rag

solr-up:
	docker rm -f $(SOLR_CONTAINER) 2>/dev/null; \
	docker run -d --name $(SOLR_CONTAINER) -p 8983:8983 solr:10.0
	$(MAKE) solr-wait
	$(MAKE) solr-setup

solr-wait:
	@echo "Waiting for Solr to be ready..."
	@for i in $$(seq 1 30); do \
		curl -s "http://localhost:8983/solr/admin/info/system?wt=json" >/dev/null 2>&1 && \
		echo "Solr ready." && break; \
		echo "  attempt $$i..."; sleep 2; \
	done

solr-setup:
	@echo "Creating core 'hybrid_rag'..."
	@docker exec $(SOLR_CONTAINER) solr create -c hybrid_rag -d _default 2>&1 | grep -v "WARNING"
	@echo "Disabling auto field creation..."
	@curl -s "http://localhost:8983/solr/hybrid_rag/config" \
		-H "Content-Type: application/json" \
		-d '{"set-user-property": {"update.autoCreateFields": "false"}}' >/dev/null
	@echo "Applying schema fields..."
	@uv run python scripts/solr_setup.py
	@echo "Solr ready: http://localhost:8983/solr/#/hybrid_rag"

solr-down:
	docker rm -f $(SOLR_CONTAINER) 2>/dev/null; true

ingest-doc:
	uv run python -m ingest.cli $(file)

query:
	uv run python -m rag.cli

test:
	uv run python -m pytest tests/ -v -k "not (test_chunk_markdown or test_tco_flatten or test_plain_text or test_tco_plain or test_fixed_size)"

test-all:
	uv run python -m pytest tests/ src/tests/ -v -k "not (test_chunk_markdown or test_tco_flatten or test_plain_text or test_tco_plain or test_fixed_size)"

pipeline:
	uv run python -m rag.cli $(q)

e2e:
	$(MAKE) solr-up
	$(MAKE) ingest-doc file=sample-contract.md
	$(MAKE) query

e2e-quick:
	$(MAKE) ingest-doc file=sample-contract.md --delete-first
	uv run python -m rag.cli "What are the payment terms?"

clean:
	rm -rf .venv chunked_output.json
