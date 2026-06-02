import unittest
from main.handle_ballot_loader import handle_ballot_loader
from helpers.types import Ballot, BallotLoadResult, InvalidBallot
from unittest.mock import patch
from pydantic import ValidationError

class TestLoadBallots(unittest.TestCase):
    maxDiff = None

    def test_load_ballots_happy(self):

        mock_happy_json_balots = BallotLoadResult(
            valid=[
                Ballot(
                    meetingId="meeting-001",
                    custodyAccountId="custody-abc",
                    isin="GB00TEST0001",
                    submissionDeadline="2026-02-15",
                    sharesInIssue=1000000
                )
            ],
            invalid=[
                InvalidBallot(
                    index=1,
                    meeting_id="meeting-002",
                    errors=[
                        {"error": "mock_error"}
                    ]
                )
            ]
        )

        with patch("main.handle_ballot_loader.load_ballots") as mock_load_ballots, self.assertLogs("main.handle_ballot_loader", level="INFO") as log_context:
            mock_load_ballots.return_value = mock_happy_json_balots
            ballot_load_result = handle_ballot_loader("tests/data/happy_ballots.json")
        self.assertEqual(ballot_load_result, mock_happy_json_balots)
        self.assertEqual(len(log_context.records), 5)

    def test_load_ballots_invalids(self):

        mock_invalid_json_balots = BallotLoadResult(
            valid=[],
            invalid=[
                InvalidBallot(
                    index=1,
                    meeting_id="meeting-001",
                    errors=[
                        {"error": "mock_error"}
                    ]
                ),
                InvalidBallot(
                    index=2,
                    meeting_id="meeting-002",
                    errors=[
                        {"error": "mock_error"}
                    ]
                ),
            ]
        )

        with patch("main.handle_ballot_loader.load_ballots") as mock_load_ballots, self.assertLogs("main.handle_ballot_loader", level="INFO") as log_context:
            mock_load_ballots.return_value = mock_invalid_json_balots
            ballot_load_result = handle_ballot_loader("tests/data/happy_ballots.json")
        self.assertEqual(ballot_load_result, mock_invalid_json_balots.invalid)
        self.assertEqual(len(log_context.records), 9)

if __name__ == '__main__':
    unittest.main()