from helpers.types import Ballot, InvalidBallot, BallotLoadResult
from main.load_ballots import load_ballots
import logging

logger = logging.getLogger(__name__)

def handle_ballot_loader(file_path: str) -> BallotLoadResult | list[InvalidBallot]:

    json_balots = load_ballots(file_path)

    logger.info("Read %s valid ballots", len(json_balots.valid))

    logger.info("Read %s invalid ballots", len(json_balots.invalid))

    for invalid in json_balots.invalid:
        logger.warning("Invalid ballot at index: %s", invalid.index)

        if invalid.meeting_id is not None:
            logger.warning("Meeting ID: %s", invalid.meeting_id)
        else:
            logger.warning("No valid meeting ID")
        
        for error in invalid.errors:
            logger.warning("error: %s", error)

    if len(json_balots.valid) <= 0:
        logger.error("No valid ballots included")
        return json_balots.invalid
    else:
        return json_balots
