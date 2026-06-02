import datetime
from helpers.types import Ballot, InvalidBallot, BallotLoadResult, BallotProcessingResult, BallotProcessingResultLists
from main.handle_ballot_loader import handle_ballot_loader
from main.process_ballot import process_ballot
import httpx
import asyncio
import logging


json_file_path = "data/ballot_data.json"
#Would be stored in AWS secrets manager or another secure storage solution
api_key = "fake_key"
MAX_CONCURRENT_BALLOTS = 5
MAX_CONCURRENT_API_CALLS = 20
API_BASE_URL = "https://api.tumelo.com"
as_of_date = datetime.today()
    
def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

async def process_all_ballots(
        ballots: list[Ballot],
        api_key: str
) -> list[BallotProcessingResultLists]:
    #Limit concurrent ballots running, would be useful to not overload APIs
    ballot_semaphore = asyncio.Semaphore(MAX_CONCURRENT_BALLOTS)
    api_semaphore = asyncio.Semaphore(MAX_CONCURRENT_API_CALLS)

    async with httpx.AsyncClient(
        base_url=API_BASE_URL,
        headers={
            "api_key": api_key
        },
        timeout=30,
        limits=httpx.Limits(
            max_connections=MAX_CONCURRENT_API_CALLS,
            max_keepalive_connections=MAX_CONCURRENT_API_CALLS
        )
    ) as client:

        async def process_with_limit(ballot: Ballot) -> BallotProcessingResultLists:
            # Safely does all the acquire and release bits
            async with ballot_semaphore:
                return await process_ballot(
                    client=client,
                    ballot=ballot,
                    base_url=API_BASE_URL,
                    api_key=api_key,
                    as_of_date=as_of_date,
                    api_semaphore=api_semaphore
                )
        
        results = await asyncio.gather(
            *(process_with_limit(ballot) for ballot in ballots)
        )
    return list(results)

async def main() -> None:
    configure_logging()

    logger = logging.getLogger(__name__)

    ballots = handle_ballot_loader(json_file_path)

    if ballots.isinstance(list[InvalidBallot]):
        raise SystemExit(0)
    
    results = await process_all_ballots(ballots=ballots.valid, api_key=api_key)

    for result in results:
        ballot_fails = result.ballots_failed
        ballot_successes = result.ballots_succeeded
        for result in ballot_successes:
            logger.info("%s: submitted, has entitlement_id: %s", result.meeting_id, result.entitlement.entitlement_id)
        for result in ballot_fails:
            logger.error("%s: failed, with error:  %s, %s", result.meeting_id, result.error.code, result.error.message)


if __name__ == "__main__":
    asyncio.run(main())

