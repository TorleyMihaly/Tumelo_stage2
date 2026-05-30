import asyncio
from dataclasses import dataclass
import httpx
from helpers.types import Ballot, Investor, Error
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

async def get_investors(
        client: httpx.AsyncClient,
        ballot: Ballot,
        api_key: str
) -> Investor | Error:
    response = await client.get(
        f"/custody-accounts/{ballot.custody_account_id}/investors",
        headers={
            "api_key": api_key
        }
    )

    if response.is_success:
        try:
            return Investor.model_validate(response.json())
        except ValidationError as e:
            return Error(
                code="500",
                message="Invalid success returned",
                details=e
            )
    try:
        return Error.model_validate(response.json())
    except ValidationError as e:
            return Error(
                code="500",
                message="Invalid failure returned",
                details=e
            )

    
