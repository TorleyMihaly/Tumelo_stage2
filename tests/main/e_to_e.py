

import asyncio
import datetime
import json
import logging
from pathlib import Path
import tempfile
import unittest
from helpers.types import Ballot, Error, BallotLoadResult
import httpx
from main.entitlement_processor import process_all_ballots_with_client
from main.handle_ballot_loader import handle_ballot_loader

mock_custody_1="mock_custody_1"
mock_custody_2="mock_custody_2"
mock_custody_3="mock_custody_3"
mock_isin = "GB00TEST0001"
mock_meeting_id_1 = "mock_meeting_id_1"
mock_meeting_id_2 = "mock_meeting_id_2"
mock_meeting_id_3 = "mock_meeting_id_3"
mock_submission_deadline = "2026-02-15"
mock_shares_in_issue = 1000
mock_investor_id_1 = "mock_investor_id_1"
mock_investor_name_1 = "mock_investor_name_1"
mock_investor_id_2 = "mock_investor_id_2"
mock_investor_name_2 = "mock_investor_name_2"
mock_investor_id_3 = "mock_investor_id_3"
mock_investor_name_3 = "mock_investor_name_3"
mock_investor_id_4 = "mock_investor_id_4"
mock_investor_name_4 = "mock_investor_name_4"
mock_investor_id_5 = "mock_investor_id_5"
mock_investor_name_5 = "mock_investor_name_5"
mock_investor_id_6 = "mock_investor_id_6"
mock_investor_name_6 = "mock_investor_name_6"
mock_quantity_1 = 1000
mock_quantity_2 = 2000
mock_quantity_3 = 3000
mock_quantity_4 = 4000
mock_quantity_5 = 5000
mock_quantity_6 = 6000
mock_as_of_date = datetime.date(2026,2,15)
mock_entitlement_id_1="mock_entitlement_id_1"
mock_entitlement_id_2="mock_entitlement_id_2"
mock_entitlement_id_3="mock_entitlement_id_3"
mock_entitlement_id_4="mock_entitlement_id_4"
mock_entitlement_id_5="mock_entitlement_id_5"
mock_entitlement_id_6="mock_entitlement_id_6"
mock_created_at=datetime.datetime(2026,2,15,0,0,0)
ballot_1 = Ballot(
            meetingId=mock_meeting_id_1,
            custodyAccountId=mock_custody_1,
            isin=mock_isin,
            submissionDeadline=mock_submission_deadline,
            sharesInIssue=mock_shares_in_issue
        )
ballot_2 = Ballot(
            meetingId=mock_meeting_id_2,
            custodyAccountId=mock_custody_2,
            isin=mock_isin,
            submissionDeadline=mock_submission_deadline,
            sharesInIssue=mock_shares_in_issue
        )
ballot_3 = Ballot(
            meetingId=mock_meeting_id_3,
            custodyAccountId=mock_custody_3,
            isin=mock_isin,
            submissionDeadline=mock_submission_deadline,
            sharesInIssue=mock_shares_in_issue
        )
mock_base_url = "https://mock.com"
mock_api_key = "mock_key"
MAX_CONCURRENT_BALLOTS = 5
MAX_CONCURRENT_API_CALLS = 20

investors_by_custody = {
    mock_custody_1: [
        {
            "investorId": mock_investor_id_1,
            "name": mock_investor_name_1
        },
        {
            "investorId": mock_investor_id_2,
            "name": mock_investor_name_2
        }
    ],
    mock_custody_2: [
        {
            "investorId": mock_investor_id_4,
            "name": mock_investor_name_4
        },
        {
            "investorId": mock_investor_id_3,
            "name": mock_investor_name_3
        },
    ],
    mock_custody_3: [
        {
            "investorId": mock_investor_id_5,
            "name": mock_investor_name_5
        },
        {
            "investorId": mock_investor_id_6,
            "name": mock_investor_name_6
        },
    ],
}

logger = logging.getLogger(__name__)

class TestEndToEndBallotProcessing(unittest.IsolatedAsyncioTestCase):

    async def test_full_ballot_flow(self) -> None:
        def mock_handler(request: httpx.Request) -> httpx.Response:
            request_seen: list[httpx.Request] = []

            if request.method == "GET" and "/investors" in request.url.path:
                parts = request.url.path.split("/")
                custody_account_id = parts[2]
                return httpx.Response(
                    status_code=200,
                    json={"investors": investors_by_custody[custody_account_id]},
                    request=request
                )
            
            if request.method == "GET" and request.url.path == "/holdings":

                investor_id = request.url.params["investorId"]
                isin = request.url.params["isin"]

                def json_body_gen(investor, quantity):
                    return {
                        "investorId": investor,
                        "isin": isin,
                        "quantity": quantity,
                        "asOfDate": mock_as_of_date.isoformat()
                    }

                if investor_id == mock_investor_id_1:
                    return httpx.Response(
                        status_code=200,
                        json=json_body_gen(mock_investor_id_1, mock_quantity_1),
                        request=request
                    )
                if investor_id == mock_investor_id_2:
                    return httpx.Response(
                        status_code=200,
                        json=json_body_gen(mock_investor_id_2, mock_quantity_2),
                        request=request
                    )
                if investor_id == mock_investor_id_3:
                    return httpx.Response(
                        status_code=200,
                        json=json_body_gen(mock_investor_id_3, mock_quantity_3),
                        request=request
                    )
                if investor_id == mock_investor_id_4:
                    return httpx.Response(
                        status_code=200,
                        json=json_body_gen(mock_investor_id_4, mock_quantity_4),
                        request=request
                    )
                if investor_id == mock_investor_id_5:
                    return httpx.Response(
                        status_code=400,
                        json={
                            "code": "400",
                            "message": "Invalid request parameters"
                        },
                        request=request
                    )
                if investor_id == mock_investor_id_6:
                    return httpx.Response(
                        status_code=200,
                        json=json_body_gen(mock_investor_id_6, mock_quantity_6),
                        request=request
                    )
                
            if request.method == "POST" and request.url.path == "/entitlements":
                
                json_body = json.loads(request.content)
                investor_id = json_body["investorId"]
                isin = json_body["isin"]

                def json_body_gen(entitlement, meeting_id, investor_id, quantity):
                    return {
                        "entitlementId": entitlement,
                        "meetingId": meeting_id,
                        "investorId": investor_id,
                        "isin": isin,
                        "quantity": quantity,
                        "createdAt": mock_created_at.isoformat()
                    }

                if investor_id == mock_investor_id_1:
                    return httpx.Response(
                        status_code=201,
                        json=json_body_gen(mock_entitlement_id_1, mock_meeting_id_1, mock_investor_id_1, mock_quantity_1),
                        request=request
                    )
                if investor_id == mock_investor_id_2:
                    return httpx.Response(
                        status_code=201,
                        json=json_body_gen(mock_entitlement_id_2, mock_meeting_id_1, mock_investor_id_2, mock_quantity_2),
                        request=request
                    )
                if investor_id == mock_investor_id_3:
                    return httpx.Response(
                        status_code=201,
                        json=json_body_gen(mock_entitlement_id_3, mock_meeting_id_2, mock_investor_id_3, mock_quantity_3),
                        request=request
                    )
                if investor_id == mock_investor_id_4:
                    return httpx.Response(
                        status_code=201,
                        json=json_body_gen(mock_entitlement_id_4, mock_meeting_id_2, mock_investor_id_4, mock_quantity_4),
                        request=request
                    )
                if investor_id == mock_investor_id_5:
                    return httpx.Response(
                        status_code=201,
                        json=json_body_gen(mock_entitlement_id_5, mock_meeting_id_3, mock_investor_id_5, mock_quantity_5),
                        request=request
                    )
                if investor_id == mock_investor_id_6:
                    return httpx.Response(
                        status_code=400,
                        json={
                            "code": "400",
                            "message": "Invalid entitlement request"
                        },
                        request=request
                    )
            
            
            
        transport = httpx.MockTransport(mock_handler)
        api_semaphore = asyncio.Semaphore(5)

        ballot_json = {
            "ballots": [
                ballot_1.model_dump(by_alias=True, mode="json"),
                ballot_2.model_dump(by_alias=True, mode="json"),
                ballot_3.model_dump(by_alias=True, mode="json")
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ballots.json"
            path.write_text(json.dumps(ballot_json))

            load_result = handle_ballot_loader(path)

            self.assertIsInstance(load_result, BallotLoadResult)
            self.assertEqual(len(load_result.valid), 3)
            self.assertEqual(len(load_result.invalid), 0)

            async with httpx.AsyncClient(
                base_url=mock_base_url,
                headers={
                    "api_key": mock_api_key
                },
                transport=transport,
                timeout=30
            ) as client:
                results = await process_all_ballots_with_client(
                    ballots=load_result.valid,
                    client=client,
                    as_of_date=mock_as_of_date,
                    max_connections=MAX_CONCURRENT_BALLOTS,
                    max_keepalive_connections=MAX_CONCURRENT_API_CALLS
                )
            
            # Recreation of logging from main but with warnings so that running the tests shows it
            for result in results:
                ballot_fails = result.ballots_failed
                ballot_successes = result.ballots_succeeded
                for result in ballot_successes:
                    logger.warning("%s: submitted, has entitlement_id: %s", result.meeting_id, result.entitlement.entitlement_id)
                for result in ballot_fails:
                    logger.warning("%s: failed, with error:  %s, %s", result.meeting_id, result.error.code, result.error.message)

        self.assertEqual(len(results), 3)

        ballot_results_1 = results[0].ballots_succeeded[0]
        ballot_results_2 = results[1].ballots_succeeded[0]
        ballot_results_3_fail_1 = results[2].ballots_failed[0]
        ballot_results_3_fail_2 = results[2].ballots_failed[1]

        self.assertTrue(ballot_results_1.success)
        self.assertEqual(ballot_results_1.meeting_id, mock_meeting_id_1)
        self.assertEqual(ballot_results_1.entitlement.entitlement_id, mock_entitlement_id_1)

        self.assertTrue(ballot_results_2.success)
        self.assertEqual(ballot_results_2.meeting_id, mock_meeting_id_2)
        self.assertEqual(ballot_results_2.entitlement.entitlement_id, mock_entitlement_id_4)

        self.assertTrue(not ballot_results_3_fail_1.success)
        self.assertEqual(ballot_results_3_fail_1.error, Error(code="400", message="Invalid request parameters"))

        self.assertTrue(not ballot_results_3_fail_2.success)
        self.assertEqual(ballot_results_3_fail_2.error, Error(code="400", message="Invalid entitlement request"))
            
