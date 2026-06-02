import asyncio
from datetime import date
import typing
import httpx
from helpers.types import BallotProcessingResult, Ballot, BallotProcessingResultLists, Investor, Error, Holding, EntitlementRequest, Entitlement, InvestorList
from main.get_holdings import get_holdings
from main.get_investors import get_investors
from main.post_entitlements import post_entitlements
import logging

logger = logging.getLogger(__name__)


async def process_ballot(
        client: httpx.AsyncClient,
        ballot: Ballot,
        as_of_date: date,
        api_semaphore: asyncio.Semaphore
) -> BallotProcessingResultLists:
    
    
    
    list_of_ballot_processing_results_fail = []
    list_of_ballot_processing_results_success = []
    
    def error_handler(response):
        if isinstance(response, Error):
            return BallotProcessingResult(
                meeting_id=ballot.meeting_id,
                success=False,
                error=response
            )
        else:
            return None

    try:
        investors: InvestorList | Error = await get_investors(
            client=client,
            ballot=ballot,
            api_semaphore=api_semaphore
        )


        error_check: None | BallotProcessingResult = error_handler(response=investors)
        if isinstance(error_check, BallotProcessingResult): 
            return error_check
        

        for investor in investors.investors:
            holding: Holding | Error = await get_holdings(
                client=client,
                ballot=ballot,
                investor_id=investor.investor_id,
                as_of_date=as_of_date,
                api_semaphore=api_semaphore
            )


            error_check: None | BallotProcessingResult = error_handler(response=holding)
            if isinstance(error_check, BallotProcessingResult):
                list_of_ballot_processing_results_fail.append(error_check)
                continue

            
            entitlement_request = EntitlementRequest(
                meetingId=ballot.meeting_id,
                investorId=investor.investor_id,
                isin=ballot.isin,
                quantity=holding.quantity
            )


            entitlement: Entitlement | Error = await post_entitlements(
                client=client,
                entitelement_request=entitlement_request,
                api_semaphore=api_semaphore
            )

            
            error_check: None | BallotProcessingResult = error_handler(response=entitlement)
            if isinstance(error_check, BallotProcessingResult):
                list_of_ballot_processing_results_fail.append(error_check)
                continue

            
            succesful_result =  BallotProcessingResult(
                meeting_id=ballot.meeting_id,
                success=True,
                entitlement=entitlement
            )

            list_of_ballot_processing_results_success.append(succesful_result)



        return BallotProcessingResultLists(
            ballots_failed=list_of_ballot_processing_results_fail,
            ballots_succeeded=list_of_ballot_processing_results_success
        )


    except Exception as e:
        logger.warning("error: %s", e)
        ballot_processing_results_fail =  BallotProcessingResult(
             meeting_id=ballot.meeting_id,
             success=False,
             error=Error(
                  code="500",
                  message="Something went wrong with processing the ballots",
                  details=str(e)
             )
        )

        list_of_ballot_processing_results_fail.append(ballot_processing_results_fail)
    
        return BallotProcessingResultLists(
            ballots_failed=list_of_ballot_processing_results_fail,
            ballots_succeeded=list_of_ballot_processing_results_success
        )