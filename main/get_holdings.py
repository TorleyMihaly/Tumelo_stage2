import asyncio
from dataclasses import dataclass
import httpx
from helpers.types import Ballot, Holding, Error
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from datetime import date, datetime

async def get_holdings(
        client: httpx.AsyncClient,
        base_url: str,
        ballot: Ballot,
        investor_id: str,
        as_of_date: date,
        api_key: str,
        api_semaphore: asyncio.Semaphore
) -> Holding | Error:
    async with api_semaphore:
        response = await client.get(
            "/holdings",
            params={
                "investorId": investor_id,
                "isin": ballot.isin,
                "asOfDate": as_of_date.isoformat()
            }
        )

    if response.is_success:
        try:
            return Holding.model_validate(response.json())
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

    
