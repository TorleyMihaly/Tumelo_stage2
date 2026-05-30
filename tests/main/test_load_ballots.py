import unittest
from main.load_ballots import load_ballots
from helpers.types import Ballot, BallotLoadResult

class TestLoadBallots(unittest.TestCase):
    maxDiff = None

    def test_happy(self):
        lsit_of_balllots = load_ballots("tests/data/happy_ballots.json")
        happy_ballot =[ Ballot(
            meetingId="meeting-001",
            custodyAccountId="custody-abc",
            isin="GB00TEST0001",
            submissionDeadline="2026-02-15",
            sharesInIssue=1000000
        )]
        self.assertEqual(lsit_of_balllots.valid, happy_ballot)

    def test_mix(self):
        lsit_of_balllots = load_ballots("tests/data/mixed_ballots.json")
        mixed_ballot = [
            Ballot(
                meetingId="meeting-001",
                custodyAccountId="custody-abc",
                isin="GB00TEST0001",
                submissionDeadline="2026-02-15",
                sharesInIssue=1000000
            )
        ]
        self.assertEqual(lsit_of_balllots.valid, mixed_ballot)

if __name__ == '__main__':
    unittest.main()