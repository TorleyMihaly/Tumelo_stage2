import asyncio
from datetime import date, datetime
import json
from main.post_entitlements import post_entitlements
from helpers.types import Ballot, Holding, Investor, Error, EntitlementRequest, Entitlement
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
mock_invalid_request_error_message = "Invalid entitlement request"
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
mock_created_at=datetime(2026,2,15,0,0,0)
mock_quantity=1500
mock_entitlement_id="mock_entitlement_id"
entitlement_request = EntitlementRequest(
            meetingId=mock_meeting_id,
            investorId=mock_investor_id,
            isin=mock_isin,
            quantity=mock_quantity
        )

class TestPostEntitlements(unittest.IsolatedAsyncioTestCase):
    maxDiff = None
   

    async def test_post_entitlements_happy(self):
        request_seen: list[httpx.Request] = []
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "POST")
            self.assertEqual(
                request.url.path,
                f"/entitlements"
            )

            request_seen.append(request)

            return httpx.Response(
                status_code=201,
                json={
                        "entitlementId": mock_entitlement_id,
                        "meetingId": mock_meeting_id,
                        "investorId": mock_investor_id,
                        "isin": mock_isin,
                        "quantity": mock_quantity,
                        "createdAt": mock_created_at.isoformat()
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
            result = await post_entitlements(
                client=client,
                entitelement_request=entitlement_request,    
                api_semaphore=api_semaphore
            )

        self.assertIsInstance(result, Entitlement)
        self.assertEqual(result.entitlement_id, mock_entitlement_id)
        self.assertEqual(result.meeting_id, mock_meeting_id)
        self.assertEqual(result.investor_id, mock_investor_id)
        self.assertEqual(result.isin, mock_isin)
        self.assertEqual(result.quantity, mock_quantity)
        self.assertEqual(result.created_at, mock_created_at)

        sent_requests = request_seen[0]

        sent_json = json.loads(sent_requests.content)

        #Checking to see if entitelement_request.model_dump(by_alias=True, mode="json") works properly
        self.assertEqual(
            sent_json,
            {
                "meetingId": mock_meeting_id,
                "investorId": mock_investor_id,
                "isin": mock_isin,
                "quantity": mock_quantity
            }
        )

    async def test_post_entitlements_error(self):
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "POST")
            self.assertEqual(
                request.url.path,
                f"/entitlements"
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
            result = await post_entitlements(
                client=client,
                entitelement_request=entitlement_request,    
                api_semaphore=api_semaphore
            )

        self.assertIsInstance(result, Error)
        self.assertEqual(result.code, mock_invalid_request_error_code)
        self.assertEqual(result.message, mock_invalid_request_error_message)

    async def test_post_entitlements_malformed_response(self):
        
        def mock_handler(request: httpx.Request) -> httpx.Response:
            #Making sure request is all good
            self.assertEqual(request.method, "POST")
            self.assertEqual(
                request.url.path,
                f"/entitlements"
            )

            return httpx.Response(
                status_code=201,
                json=[{
                        "entitlementId": mock_entitlement_id,
                        "meetingId": mock_meeting_id,
                        "investorId": mock_investor_id,
                        "isin": mock_isin,
                        "quantity": mock_quantity,
                        "createdAt": mock_created_at.isoformat()
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
            result = await post_entitlements(
                client=client,
                entitelement_request=entitlement_request,    
                api_semaphore=api_semaphore
            )

        self.assertIsInstance(result, Error)
        self.assertEqual(result.code, mock_malformed_error_code)
        self.assertEqual(result.message, mock_malformed_error_message)

if __name__ == '__main__':
    unittest.main()

