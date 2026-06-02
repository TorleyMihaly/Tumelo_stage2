import asyncio
from datetime import date
from main.get_holdings import get_holdings
from helpers.types import Ballot, Holding, Error
import unittest
import httpx

mock_base_url = "https://mock.com"
mock_custody_account_id: str = "mock_acc_id"
mock_api_key = "mock_key"
mock_investor_id = "mock_investor_id"
mock_meeting_id = "mock_meeting_id"
mock_isin = "GB00TEST0001"
mock_submission_deadline = "2026-02-15"
mock_shares_in_issue = 1000
mock_invalid_request_error_code = "400"
mock_invalid_request_error_message = "Invalid request parameters"
mock_malformed_error_code = "500"
mock_malformed_error_message = "Invalid success returned"
api_semaphore = asyncio.Semaphore(1)
ballot = Ballot(
            meetingId=mock_meeting_id,
            custodyAccountId=mock_custody_account_id,
            isin=mock_isin,
            submissionDeadline=mock_submission_deadline,
            sharesInIssue=mock_shares_in_issue
        )
investor_id="mock_investor_id"
mock_as_of_date=date(2026,2,15)
mock_quantity=1500

class TestGetHoldings(unittest.IsolatedAsyncioTestCase):
    maxDiff = None
   

    async def test_get_holdings_happy(self):
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "GET")
            self.assertEqual(
                request.url.path,
                f"/holdings"
            )

            return httpx.Response(
                status_code=200,
                json={
                        "investorId": mock_investor_id,
                        "isin": mock_isin,
                        "quantity": mock_quantity,
                        "asOfDate": mock_as_of_date.isoformat()
                    },
                request=request
            )
        
        transport = httpx.MockTransport(mock_handler)

        async with httpx.AsyncClient(
            base_url=mock_base_url,
            headers={
                "api_key": mock_api_key
            },
            transport=transport
        ) as client:
            result = await get_holdings(
                client=client,
                investor_id=investor_id,
                ballot=ballot,
                as_of_date=mock_as_of_date,
                api_semaphore=api_semaphore
            )

        self.assertIsInstance(result, Holding)
        self.assertEqual(result.investor_id, mock_investor_id)
        self.assertEqual(result.isin, mock_isin)
        self.assertEqual(result.quantity, mock_quantity)
        self.assertEqual(result.as_of_date, mock_as_of_date)

    async def test_get_holdings_error(self):
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "GET")
            self.assertEqual(
                request.url.path,
                f"/holdings"
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

        async with httpx.AsyncClient(
            base_url=mock_base_url,
            headers={
                "api_key": mock_api_key
            },
            transport=transport
        ) as client:
            result = await get_holdings(
                client=client,
                investor_id=investor_id,
                ballot=ballot,
                as_of_date=mock_as_of_date,
                api_semaphore=api_semaphore
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
                f"/holdings"
            )

            return httpx.Response(
                status_code=200,
                json=[{
                        "investorId": mock_investor_id,
                        "isin": mock_isin,
                        "quantity": mock_quantity,
                        "asOfDate": mock_as_of_date.isoformat()
                    }],
                request=request
            )
        
        transport = httpx.MockTransport(mock_handler)

        async with httpx.AsyncClient(
            base_url=mock_base_url,
            headers={
                "api_key": mock_api_key
            },
            transport=transport
        ) as client:
            result = await get_holdings(
                client=client,
                investor_id=investor_id,
                ballot=ballot,
                as_of_date=mock_as_of_date,
                api_semaphore=api_semaphore
            )

        self.assertIsInstance(result, Error)
        self.assertEqual(result.code, mock_malformed_error_code)
        self.assertEqual(result.message, mock_malformed_error_message)

if __name__ == '__main__':
    unittest.main()

