# Tumelo_stage2
Task for tumelo

Project structure:
entitlement_process contains main()
--> process_all_ballots()
    --->process_ballot() for each ballot
        --->Each ballot calls get_investors(), get_holdings(), post_entitlements()
            ---> post_entitlements() sends Entitlement Request and returns Entitlements
---> Each Entitlement or Error is returned and logged


To test each function:
    Run unit tests:
    python -m unittest tests.main.test_load_ballots
    python -m unittest tests.main.test_get_investor
    python -m unittest tests.main.test_post_entitlements
    python -m unittest tests.main.test_process_ballot
    python -m unittest tests.main.test_get_holdings
    python -m unittest tests.main.test_handle_ballot_loader

To run (basically)End to end test:
    python -m unittest tests.main.e_to_e

Improvements with more time:
    - Better test coverage, covers more cases
    - Return each potential Entitlement that failed as a list for fixing and rerun
    - Refactor types to make them more robust and less confusing
    - Better logging coverage
    - Refactor error handling so that actual errors can be raised and they get handled at the top
    - Take entitlement_processor apart into two different files
    - Improve folder structure
    - Get linter onto the project
    - Get import manager onto the project


installed modules:
httpx
pydantic
pytest pytest-asyncio
pytest-httpx

Assumptions:
isin regex is "^[A-Z]{2}[A-Z0-9]{10}$"
asOfDate is current date
All API's have same base URL

