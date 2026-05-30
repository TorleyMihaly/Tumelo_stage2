from datetime import date
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

    @field_validator("isin", mode="before")
    @classmethod
    def normalise_isin(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

@dataclass(frozen=True)
class InvalidBallot:
    index: int
    meeting_id: str | None
    errors: list[dict[str]]

@dataclass(frozen=True)
class BallotLoadResult:
    valid: list[Ballot]
    invalid: list[InvalidBallot]


