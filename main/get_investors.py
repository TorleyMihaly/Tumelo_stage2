import asyncio
from dataclasses import dataclass
import httpx
from helpers.types import Ballot, Investor, Error, InvestorList
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

async def get_investors(
        client: httpx.AsyncClient,
        ballot: Ballot,
        api_semaphore: asyncio.Semaphore
) -> list[Investor] | Error:
    async with api_semaphore:
        response = await client.get(
            f"/custody-accounts/{ballot.custody_account_id}/investors",
        )

    investor_list: list[Investor] = []

    if response.is_success:
        try:
            InvestorList.model_validate(response.json())                 
            for investor in response.json()["investors"]:
                investor_list.append(Investor.model_validate(investor))
            return investor_list
        except ValidationError as e:
            return Error(
                code="500",
                message="Invalid success returned",
                details=str(e)
            )
    try:
        return Error.model_validate(response.json())
    except ValidationError as e:
            return Error(
                code="500",
                message="Invalid failure returned",
                details=str(e)
            )

    
