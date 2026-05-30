import asyncio
from dataclasses import dataclass
import httpx
from helpers.types import Ballot, Holding, Error
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from datetime import date, datetime

async def get_holdings(
        client: httpx.AsyncClient,
        ballot: Ballot,
        investor_id: str,
        as_of_date: date,
        api_key: str
) -> Holding | Error:
    response = await client.get(
        f"/holdings",
        headers={
            "api_key": api_key
        },
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

    
