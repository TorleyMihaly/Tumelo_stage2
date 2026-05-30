from datetime import date, datetime
from pathlib import Path
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

class Ballot(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_by_name=True,
        validate_by_alias=True,
        str_strip_whitespace=True,
    )

    meeting_id: str = Field(
        alias="meetingId",
        min_length=1,
        strict=True
    )

    custody_account_id: str = Field(
        alias="custodyAccountId",
        min_length=1,
        strict=True
    )

    isin: str = Field(
        alias="isin",
        pattern=r"^[A-Z]{2}[A-Z0-9]{10}$",
        strict=True
    )

    submission_deadline: date = Field(
        alias="submissionDeadline"
    )

    shares_in_issue: int = Field(
        alias="sharesInIssue",
        gt=0,
        strict=True
    )
    # gt=0 means it has to be greater than 0

    #commented out for strict validation
    # @field_validator("isin", mode="before")
    # @classmethod
    # def normalise_isin(cls, value: object) -> object:
    #     if isinstance(value, str):
    #         return value.strip().upper()
    #     return value

@dataclass(frozen=True)
class InvalidBallot:
    index: int
    meeting_id: str | None
    errors: list[dict[str]]

@dataclass(frozen=True)
class BallotLoadResult:
    valid: list[Ballot]
    invalid: list[InvalidBallot]

class Investor(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_by_name=True,
        validate_by_alias=True
    )

    investor_id: str = Field(
        alias="investorId",
        min_length=1,
        strict=True
    )

    name: str = Field(
        alias="name",
        min_length=1,
        strict=True
    )

class Holding(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_by_name=True,
        validate_by_alias=True
    )

    investor_id: str = Field(
        alias="investorId",
        min_length=1,
        strict=True
    )

    isin: str = Field(
        alias="isin",
        pattern=r"^[A-Z]{2}[A-Z0-9]{10}$",
        strict=True
    )

    quantity: float = Field(
        alias="quantity",
        gt=0,
        strict=True
    )

    as_of_date: date = Field(
        alias="asOfDate"
    )

class EntitlementRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_by_name=True,
        validate_by_alias=True
    )

    meeting_id: str = Field(
        alias="meetingId",
        min_length=1,
        strict=True
    )

    investor_id: str = Field(
        alias="investorId",
        min_length=1,
        strict=True
    )

    isin: str = Field(
        alias="isin",
        pattern=r"^[A-Z]{2}[A-Z0-9]{10}$",
        strict=True
    )

    quantity: float = Field(
        alias="quantity",
        gt=0,
        strict=True
    )

class Entitlement(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_by_name=True,
        validate_by_alias=True
    )

    entitlement_id: str = Field(
        alias="entitlementId",
        min_length=1,
        strict=True
    )

    meeting_id: str = Field(
        alias="meetingId",
        min_length=1,
        strict=True
    )

    investor_id: str = Field(
        alias="investorId",
        min_length=1,
        strict=True
    )

    isin: str = Field(
        alias="isin",
        pattern=r"^[A-Z]{2}[A-Z0-9]{10}$",
        strict=True
    )

    quantity: float = Field(
        alias="quantity",
        gt=0,
        strict=True
    )

    created_at: datetime = Field(
        alias="createdAt"
    )

class Error(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_by_name=True,
        validate_by_alias=True
    )

    code: str = Field(
        alias="code",
        min_length=1,
        strict=True
    )

    message: str = Field(
        alias="message",
        min_length=1,
        strict=True
    )

    details: str | None = Field(
        alias="details",
        default=None,
        strict=True
    )


