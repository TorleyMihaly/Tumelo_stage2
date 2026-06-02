import logging
from helpers.types import Ballot, InvalidBallot, BallotLoadResult
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
import json

logger = logging.getLogger(__name__)

def load_ballots(path: str) -> BallotLoadResult:
    path = Path(path)
    try:
        raw_ballot_file = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Bad JSON file: {e}")
    
    if not isinstance(raw_ballot_file, dict):
        raise ValueError("JSON needs to include dict that holds the list ballots")
    
    raw_ballots = raw_ballot_file.get("ballots")

    if not isinstance(raw_ballots, list):
        raise ValueError("JSON needs to include list of ballots")
    
    valid_ballots: list[Ballot] = []
    #Invalid ballots will be kept for logging purposes
    invalid_ballots: list[InvalidBallot] = []

    #loop through the list of ballots checking each one
    for index, raw_ballot in enumerate(raw_ballots):
        try:
            ballot = Ballot.model_validate(raw_ballot)
        except ValidationError as error:
            #set meeting ID for invalid ballot
            meeting_id = None
            #Check if invalid ballot has meeting ID
            if isinstance(raw_ballot , dict):
                raw_meeting_id = raw_ballot.get("meetingId")
                if isinstance(raw_meeting_id, str):
                    meeting_id = raw_meeting_id
            
            invalid_ballots.append(
                InvalidBallot(
                    index=index,
                    meeting_id=meeting_id,
                    errors=error.errors(
                        #include_input=False,
                        include_url=False
                    )
                )
            )
        # Else needed otherwise multiples of valid ballots will be appended
        else:
            if ballot in valid_ballots:
                logger.warning("Duplicate ballot: %s", ballot.meeting_id)
            else:
                valid_ballots.append(ballot)

    return BallotLoadResult(
        valid=valid_ballots,
        invalid=invalid_ballots
    )