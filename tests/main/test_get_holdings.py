from main.get_investors import get_investors
from helpers.types import Ballot, Investor, Error
import unittest
import httpx

mock_base_url = "https://mock.com"
mock_custody_account_id: str = "mock_acc_id"
mock_api_key = "mock_key"
mock_investor_id = "mock_investor_id"
mock_investor_name = "mock_investor_name"
mock_meeting_id = "mock_meeting_id"
mock_isin = "GB00TEST0001"
mock_submission_deadline = "2026-02-15"
mock_shares_in_issue = 1000
mock_invalid_request_error_code = "400"
mock_invalid_request_error_message = "Invalid custody account ID format"
mock_malformed_error_code = "500"
mock_malformed_error_message = "Invalid success returned"

class TestGetHoldings(unittest.IsolatedAsyncioTestCase):
    maxDiff = None
   

    async def test_get_holdings_happy(self):
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "GET")
            self.assertEqual(
                request.url.path,
                f"/custody-accounts/{mock_custody_account_id}/investors"
            )

            return httpx.Response(
                status_code=200,
                json={"investors": [
                        {
                            "investorId": mock_investor_id,
                            "name": mock_investor_name
                        }
                    ]
                },
                request=request
            )
        
        transport = httpx.MockTransport(mock_handler)

        ballot = Ballot(
            meetingId=mock_meeting_id,
            custodyAccountId=mock_custody_account_id,
            isin=mock_isin,
            submissionDeadline=mock_submission_deadline,
            sharesInIssue=mock_shares_in_issue
        )

        async with httpx.AsyncClient(
            base_url=mock_base_url,
            headers={
                "api_key": mock_api_key
            },
            transport=transport
        ) as client:
            result = await get_investors(
                client=client,
                base_url=mock_base_url,
                ballot=ballot,
                api_key=mock_api_key
            )

        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(item, Investor) for item in result))
        for investor in result:
            self.assertEqual(investor.investor_id, mock_investor_id)
            self.assertEqual(investor.name, mock_investor_name)

    async def test_get_holdings_error(self):
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "GET")
            self.assertEqual(
                request.url.path,
                f"/custody-accounts/{mock_custody_account_id}/investors"
            )

            return httpx.Response(
                status_code=400,
                json={
                        "code": mock_invalid_request_error_code,
                        "message": mock_invalid_request_error_message
                    },
                request=request
            )
        
        transport = httpx.MockTransport(mock_handler)

        ballot = Ballot(
            meetingId=mock_meeting_id,
            custodyAccountId=mock_custody_account_id,
            isin=mock_isin,
            submissionDeadline=mock_submission_deadline,
            sharesInIssue=mock_shares_in_issue
        )

        async with httpx.AsyncClient(
            base_url=mock_base_url,
            headers={
                "api_key": mock_api_key
            },
            transport=transport
        ) as client:
            result = await get_investors(
                client=client,
                base_url=mock_base_url,
                ballot=ballot,
                api_key=mock_api_key
            )

        self.assertIsInstance(result, Error)
        self.assertEqual(result.code, mock_invalid_request_error_code)
        self.assertEqual(result.message, mock_invalid_request_error_message)

    async def test_get_holdings_malformed_response(self):
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "GET")
            self.assertEqual(
                request.url.path,
                f"/custody-accounts/{mock_custody_account_id}/investors"
            )

            return httpx.Response(
                status_code=200,
                json={
                        "investorId": mock_investor_id,
                        "name": mock_investor_name
                    },
                request=request
            )
        
        transport = httpx.MockTransport(mock_handler)

        ballot = Ballot(
            meetingId=mock_meeting_id,
            custodyAccountId=mock_custody_account_id,
            isin=mock_isin,
            submissionDeadline=mock_submission_deadline,
            sharesInIssue=mock_shares_in_issue
        )

        async with httpx.AsyncClient(
            base_url=mock_base_url,
            headers={
                "api_key": mock_api_key
            },
            transport=transport
        ) as client:
            result = await get_investors(
                client=client,
                base_url=mock_base_url,
                ballot=ballot,
                api_key=mock_api_key
            )

        self.assertIsInstance(result, Error)
        self.assertEqual(result.code, mock_malformed_error_code)
        self.assertEqual(result.message, mock_malformed_error_message)

if __name__ == '__main__':
    unittest.main()

