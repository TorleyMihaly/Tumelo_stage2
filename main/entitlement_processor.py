import datetime
from helpers.types import Ballot, InvalidBallot, BallotLoadResult, BallotProcessingResult
from main.handle_ballot_loader import handle_ballot_loader
from main.process_ballot import process_ballot
import httpx
import asyncio


json_file_path = "data/ballot_data.json"
#Would be stored in AWS secrets manager or another secure storage solution
api_key = "fake_key"
MAX_CONCURRENT_BALLOTS = 10
API_BASE_URL = "https://api.tumelo.com"
as_of_date = datetime.today()
    


async def process_all_ballots(
        ballots: list[Ballot]
) -> list[BallotProcessingResult]:
    #Limit concurrent ballots running, would be useful to not overload APIs
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_BALLOTS)

    async with httpx.AsyncClient(timeout=30) as client:

        async def process_with_limit(ballot: Ballot) -> BallotProcessingResult:
            # Safely does all the acquire and release bits
            async with semaphore:
                return await process_ballot(
                    client=client,
                    ballot=ballot,
                    base_url=API_BASE_URL,
                    api_key=api_key,
                    as_of_date=as_of_date
                )
        
        results = await asyncio.gather(
            *(process_with_limit(ballot) for ballot in ballots)
        )
    return list(results)

async def main() -> None:
    ballots = handle_ballot_loader(json_file_path)

    if ballots.isinstance(list[InvalidBallot]):
        raise SystemExit(0)
    
    results = await process_all_ballots(ballots=ballots.valid)

    for result in results:
        if result.success:
            print(f"{result.meeting_id}: submitted, has entitlrent_id: {result.entitlement.entitlement_id}")
        else:
            print(f"{result.meeting_id}: failed, with error: {result.error.code}, {result.error.message}")


if __name__ == "__main__":
    asyncio.run(main())

