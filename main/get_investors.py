import asyncio
import logging
import httpx
from helpers.types import Ballot, Investor, Error, InvestorList
from pydantic import ValidationError

logger = logging.getLogger(__name__)

async def get_investors(
        client: httpx.AsyncClient,
        ballot: Ballot,
        api_semaphore: asyncio.Semaphore
) -> InvestorList | Error:
    async with api_semaphore:
        response = await client.get(
            f"/custody-accounts/{ballot.custody_account_id}/investors",
        )

    investor_list: list[Investor] = []

    logger.info("Running get_investors for %s",ballot.custody_account_id)

    if response.is_success:
        try:
            InvestorList.model_validate(response.json())                 
            for investor in response.json()["investors"]:
                investor_list.append(Investor.model_validate(investor))
            return InvestorList(investors=investor_list)
        except ValidationError as e:
            logger.warning("ValidationError f0r get_investors for %s",ballot.custody_account_id)
            return Error(
                code="500",
                message="Invalid success returned",
                details=str(e)
            )
    try:
        return Error.model_validate(response.json())
    except ValidationError as e:
            logger.warning("Invalid failure for get_investors for %s",ballot.custody_account_id)
            return Error(
                code="500",
                message="Invalid failure returned",
                details=str(e)
            )

    
