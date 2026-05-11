CONFIG ?= configs/lab.yaml
OUTPUT ?= outputs/metrics.json

install:
	pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src

run-scenarios:
	python -m langgraph_agent_lab.cli run-scenarios --config $(CONFIG) --output $(OUTPUT)

grade-local:
	python -m langgraph_agent_lab.cli validate-metrics --metrics $(OUTPUT)

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov dist build *.egg-info outputs/*.json
