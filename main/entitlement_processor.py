from helpers.types import Ballot, InvalidBallot, BallotLoadResult
from main.load_ballots import load_ballots


json_file_path = "data/ballot_data.json"
api_key = "fake_key"

def handle_ballot_loader(file_path: str) -> BallotLoadResult | None:

    json_balots = load_ballots(file_path)

    print(f"Read {len(json_balots.valid)} valid ballots")

    print(f"Read {len(json_balots.invalid)} invalid ballots")

    for invalid in json_balots.invalid:
        print(f"Invalid ballot at index: {invalid.index}")

        if invalid.meeting_id is not None:
            print(f"Meeting ID: {invalid.meeting_id}")
        else:
            print("No valid meeting ID")
        
        for error in invalid.errors:
            print(error)

    if len(json_balots.valid) <= 0:
        print("No valid ballots included")
        raise SystemExit(0)
    else:
        return json_balots
    
ballots = handle_ballot_loader(json_file_path)




