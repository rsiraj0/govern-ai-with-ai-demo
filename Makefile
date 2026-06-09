.PHONY: fixture score test clean

# Generate the labelled illustrative run (no keys, no network).
fixture:
	python scripts/make_illustrative_fixture.py

# Score whatever is in data/runs/run.json and write results/table.{md,csv}.
score:
	python -m src.report

# Run the scorer's tests.
test:
	pytest -q

clean:
	rm -f results/table.md results/table.csv
