import asyncio
from dataclasses import dataclass
import json
import logging
import httpx
from helpers.types import Ballot, Holding, Error, EntitlementRequest, Entitlement
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from datetime import date, datetime


logger = logging.getLogger(__name__)
async def post_entitlements(
        client: httpx.AsyncClient,
        entitelement_request: EntitlementRequest,
        api_semaphore: asyncio.Semaphore
) -> Entitlement | Error:

    json_entitlement=entitelement_request.model_dump(by_alias=True, mode="json")


    async with api_semaphore:
        response = await client.post(
            "/entitlements",
            json=entitelement_request.model_dump(by_alias=True, mode="json")
        )

    logger.info("Running post_entitlements for investor_id: %s", entitelement_request.investor_id)
    

    if response.is_success:
        try:
            return Entitlement.model_validate(response.json())
        except ValidationError as e:
            logger.warning("ValidationError for post_entitlements for investor_id: %s", entitelement_request.investor_id)
            return Error(
                code="500",
                message="Invalid success returned",
                details=str(e)
            )
    try:
        return Error.model_validate(response.json())
    except ValidationError as e:
            logger.warning("Invalid failure for post_entitlements for investor_id: %s", entitelement_request.investor_id)
            return Error(
                code="500",
                message="Invalid failure returned",
                details=str(e)
            )

    
