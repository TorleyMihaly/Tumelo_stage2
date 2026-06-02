import asyncio
from datetime import date
from main.process_ballot import process_ballot
from helpers.types import Ballot, Holding, Investor, Error, InvestorList, EntitlementRequest, Entitlement, BallotProcessingResultLists
import unittest
import httpx
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace


api_semaphore = asyncio.Semaphore(1)
mock_base_url = "https://mock.com"
investor_id_1 = "investor-001"
investor_id_2 = "investor-002"
meeting_id="meeting-001"
custody_account_id="custody-abc"
isin="GB00TEST0001"
submission_deadline=date(2026,2,15)
shares_in_issue=1000000
holding_quantity_1=1000
holding_quantity_2=2000
as_of_date=date(2026,2,15)
created_at=date(2026,2,15)
entitlement_id_1 = "entitlement-id-001"
entitlement_id_2 = "entitlement-id-002"
ballot = Ballot(
    meetingId=meeting_id,
    custodyAccountId=custody_account_id,
    isin=isin,
    submissionDeadline=submission_deadline,
    sharesInIssue=shares_in_issue
)
mock_invalid_request_error_code = "400"
mock_invalid_request_error_message = "Invalid entitlement request"

class TestProcessBallot(unittest.IsolatedAsyncioTestCase):
    async def test_process_ballot_happy(self) -> None:    
        investor_1 = Investor(
            investor_id=investor_id_1,
            name="investor_name-001"
        )

        investor_2 = Investor(
            investor_id=investor_id_2,
            name="investor_name-002"
        )

        investor_response = InvestorList(
            investors=[investor_1, investor_2]
        )

        holdings_response_1 = Holding(
            investorId=investor_id_1,
            isin=isin,
            quantity=holding_quantity_1,
            asOfDate=as_of_date
        )

        holdings_response_2 = Holding(
            investorId=investor_id_2,
            isin=isin,
            quantity=holding_quantity_2,
            asOfDate=as_of_date
        )

        entitlement_response_1 = Entitlement(
            entitlementId=entitlement_id_1,
            meetingId=meeting_id,
            investorId=investor_id_1,
            isin=isin,
            quantity=holding_quantity_1,
            createdAt=created_at
        )

        entitlement_response_2 = Entitlement(
            entitlementId=entitlement_id_2,
            meetingId=meeting_id,
            investorId=investor_id_2,
            isin=isin,
            quantity=holding_quantity_2,
            createdAt=created_at
        )


        async with httpx.AsyncClient(
            base_url=mock_base_url
        ) as client:
            
            with (
                patch(
                    "main.process_ballot.get_investors"
                ) as mock_get_investors,
                patch(
                    "main.process_ballot.get_holdings"
                ) as mock_get_holdings,
                patch(
                    "main.process_ballot.post_entitlements"
                ) as mock_post_entitlements,
            ): 
                mock_get_investors.return_value = investor_response
                mock_get_holdings.side_effect = [
                    holdings_response_1,
                    holdings_response_2
                ]
                mock_post_entitlements.side_effect = [
                    entitlement_response_1,
                    entitlement_response_2
                ]

                result = await process_ballot(
                    client=client,
                    ballot=ballot,
                    as_of_date=as_of_date,
                    api_semaphore=api_semaphore
                )
        
        self.assertIsInstance(result, BallotProcessingResultLists)
        self.assertEqual(len(result.ballots_succeeded), 2)
        self.assertEqual(result.ballots_succeeded[0].meeting_id, meeting_id)
        self.assertEqual(result.ballots_succeeded[1].meeting_id, meeting_id)
        self.assertEqual(result.ballots_succeeded[0].entitlement.entitlement_id, entitlement_id_1)
        self.assertEqual(result.ballots_succeeded[1].entitlement.entitlement_id, entitlement_id_2)

    async def test_process_ballot_bad_entitlement_post(self) -> None:    
        investor_1 = Investor(
            investor_id=investor_id_1,
            name="investor_name-001"
        )

        investor_2 = Investor(
            investor_id=investor_id_2,
            name="investor_name-002"
        )

        investor_response = InvestorList(
            investors=[investor_1, investor_2]
        )

        holdings_response_1 = Holding(
            investorId=investor_id_1,
            isin=isin,
            quantity=holding_quantity_1,
            asOfDate=as_of_date
        )

        holdings_response_2 = Holding(
            investorId=investor_id_2,
            isin=isin,
            quantity=holding_quantity_2,
            asOfDate=as_of_date
        )

        entitlement_response_1 = Entitlement(
            entitlementId=entitlement_id_1,
            meetingId=meeting_id,
            investorId=investor_id_1,
            isin=isin,
            quantity=holding_quantity_1,
            createdAt=created_at
        )

        entitlement_response_2 = Error(
            code=mock_invalid_request_error_code,
            message=mock_invalid_request_error_message
        )


        async with httpx.AsyncClient(
            base_url=mock_base_url
        ) as client:
            
            with (
                patch(
                    "main.process_ballot.get_investors"
                ) as mock_get_investors,
                patch(
                    "main.process_ballot.get_holdings"
                ) as mock_get_holdings,
                patch(
                    "main.process_ballot.post_entitlements"
                ) as mock_post_entitlements,
            ): 
                mock_get_investors.return_value = investor_response
                mock_get_holdings.side_effect = [
                    holdings_response_1,
                    holdings_response_2
                ]
                mock_post_entitlements.side_effect = [
                    entitlement_response_1,
                    entitlement_response_2
                ]

                result = await process_ballot(
                    client=client,
                    ballot=ballot,
                    as_of_date=as_of_date,
                    api_semaphore=api_semaphore
                )
        
        self.assertIsInstance(result, BallotProcessingResultLists)
        self.assertEqual(len(result.ballots_failed), 1)
        self.assertEqual(len(result.ballots_succeeded), 1)
        self.assertEqual(result.ballots_succeeded[0].success, True)
        self.assertEqual(result.ballots_failed[0].success, False)
        self.assertTrue(result.ballots_succeeded[0].entitlement.entitlement_id, entitlement_id_1)
        self.assertTrue(result.ballots_failed[0].error.code, mock_invalid_request_error_code)

    async def test_process_ballot_bad_1_bad_1_good(self) -> None:    
        investor_1 = Investor(
            investor_id=investor_id_1,
            name="investor_name-001"
        )

        investor_2 = Investor(
            investor_id=investor_id_2,
            name="investor_name-002"
        )

        investor_response = InvestorList(
            investors=[investor_1, investor_2]
        )

        holdings_response_1 = Holding(
            investorId=investor_id_1,
            isin=isin,
            quantity=holding_quantity_1,
            asOfDate=as_of_date
        )

        holdings_response_2 = Holding(
            investorId=investor_id_2,
            isin=isin,
            quantity=holding_quantity_2,
            asOfDate=as_of_date
        )

        entitlement_response_1 = Error(
            code=mock_invalid_request_error_code,
            message=mock_invalid_request_error_message
        )

        entitlement_response_2 = Error(
            code=mock_invalid_request_error_code,
            message=mock_invalid_request_error_message
        )


        async with httpx.AsyncClient(
            base_url=mock_base_url
        ) as client:
            
            with (
                patch(
                    "main.process_ballot.get_investors"
                ) as mock_get_investors,
                patch(
                    "main.process_ballot.get_holdings"
                ) as mock_get_holdings,
                patch(
                    "main.process_ballot.post_entitlements"
                ) as mock_post_entitlements,
            ): 
                mock_get_investors.return_value = investor_response
                mock_get_holdings.side_effect = [
                    holdings_response_1,
                    holdings_response_2
                ]
                mock_post_entitlements.side_effect = [
                    entitlement_response_1,
                    entitlement_response_2
                ]

                result = await process_ballot(
                    client=client,
                    ballot=ballot,
                    as_of_date=as_of_date,
                    api_semaphore=api_semaphore
                )
        
        self.assertIsInstance(result, BallotProcessingResultLists)
        self.assertEqual(len(result.ballots_failed), 2)
        self.assertEqual(result.ballots_failed[0].success, False)
        self.assertEqual(result.ballots_failed[1].success, False)
        self.assertTrue(result.ballots_failed[0].error.code, mock_invalid_request_error_code)
        self.assertTrue(result.ballots_failed[1].error.code, mock_invalid_request_error_code)



