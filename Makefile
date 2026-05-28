PYTHON ?= python3
MIN_PYTHON_MAJOR ?= 3
MIN_PYTHON_MINOR ?= 10
MAX_PYTHON_MAJOR ?= 3
MAX_PYTHON_MINOR ?= 12

.PHONY: help check-python setup reproduce verify smoke clean clean-pdfs manifests

help:
	@echo "Available targets:"
	@echo "  setup      Install pinned dependencies"
	@echo "  reproduce  Run full end-to-end replication pipeline"
	@echo "  verify     Verify generated outputs against expected_outputs.yaml"
	@echo "  smoke      Run a fast smoke replication and verification"
	@echo "  clean-pdfs Remove generated PDF table previews"
	@echo "  clean      Remove generated outputs"
	@echo ""
	@echo "Interpreter notes:"
	@echo "  - Supported Python range: $(MIN_PYTHON_MAJOR).$(MIN_PYTHON_MINOR) to $(MAX_PYTHON_MAJOR).$(MAX_PYTHON_MINOR)"
	@echo "  - Override interpreter per run, for example: make PYTHON=python3.11 smoke"

check-python:
	@$(PYTHON) -c 'import sys; lo=($(MIN_PYTHON_MAJOR),$(MIN_PYTHON_MINOR)); hi=($(MAX_PYTHON_MAJOR),$(MAX_PYTHON_MINOR)); ver=sys.version_info[:2]; exe=sys.executable; ok=(lo <= ver <= hi); print(f"Using {exe} (Python {ver[0]}.{ver[1]})"); print(f"ERROR: Unsupported Python version. Expected {lo[0]}.{lo[1]} to {hi[0]}.{hi[1]}.") if not ok else None; print("Hint: run with make PYTHON=python3.11 <target>") if not ok else None; raise SystemExit(0 if ok else 1)'

setup: check-python
	$(PYTHON) -m pip install -r requirements-lock.txt

reproduce: check-python
	PYTHONPATH=. $(PYTHON) replication/reproduce_all.py --config replication/run_config.yaml

verify: check-python
	PYTHONPATH=. $(PYTHON) replication/verify_outputs.py --expected replication/expected_outputs.yaml

smoke: check-python
	PYTHONPATH=. $(PYTHON) replication/reproduce_all.py --config replication/run_config.yaml --smoke
	PYTHONPATH=. $(PYTHON) replication/verify_outputs.py --expected replication/expected_outputs.yaml --smoke

clean-pdfs:
	rm -f results/paper_tables_pdf/*.pdf

clean:
	rm -rf results/tables/*.csv results/figures/*.png results/diagnostics/*.csv results/qualitative/*.csv results/descriptive/*.csv results/descriptive/*.md results/descriptive/appendix_b_figures/*.png results/descriptive/appendix_b_tables/*.csv results/manifests/*.csv
	rm -f results/paper_tables_pdf/*.pdf results/runtime/*.json results/runtime/*.csv results/runtime/*.md results/reproduction_report.md
	rm -rf paper/tables/*.tex paper/figures/*.png paper/generated_sections/*.md
	rm -f results/logs/reproduction.log results/logs/last_run_metadata.json
