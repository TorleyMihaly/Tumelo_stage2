# Tumelo_stage2
Task for tumelo

./venv/scripts/activate

installed:
httpx
pydantic
pytest pytest-asyncio
pytest-httpx

Assumptions:
isin regex is "^[A-Z]{2}[A-Z0-9]{10}$"
asOfDate is current date
All API's have same base URL

Run unit tests:
python -m unittest tests.main.test_load_ballots