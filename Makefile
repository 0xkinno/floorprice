.PHONY: test style reproduce sims facts clean
test:
	pytest -q
style:
	python scripts/check_style.py
sims:
	python -m floorprice.cli sims
# Rebuilds every number and figure from cached raw outputs. No keys, no network.
reproduce:
	FLOORPRICE_OFFLINE=1 python -m floorprice.cli run
	python -m floorprice.cli sims
	python scripts/facts.py
	python scripts/numbers.py
	python -m floorprice.figures
facts:
	python scripts/facts.py && python scripts/numbers.py
