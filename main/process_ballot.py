from datetime import date
import httpx
from helpers.types import BallotProcessingResult, Ballot, Investor, Error, Holding, EntitlementRequest, Entitlement, InvestorList
from main.get_holdings import get_holdings
from main.get_investors import get_investors
from main.post_entitlements import post_entitlements



async def process_ballot(
        client: httpx.AsyncClient,
        ballot: Ballot,
        base_url: str,
        api_key: str,
        as_of_date: date
) -> BallotProcessingResult:
    
    def error_handler(response):
        if response.isinstance(Error):
                return BallotProcessingResult(
                    meeting_id=ballot.meeting_id,
                    success=False,
                    error=Error
                )

    try:
        investor: InvestorList | Error = await get_investors(
            client=client,
            base_url=base_url,
            ballot=ballot,
            api_key=api_key
        )
        


        error_check: None | BallotProcessingResult = error_handler(response=investor)
        if error_check.isinstance(BallotProcessingResult):
             return error_check
        
        holding: Holding | Error = await get_holdings(
            client=client,
            base_url=base_url,
            ballot=ballot,
            api_key=api_key,
            investor_id=investor.investor_id,
            as_of_date=as_of_date
        )

        error_check: None | BallotProcessingResult = error_handler(holding=holding)
        if error_check.isinstance(BallotProcessingResult):
             return error_check
        
        entitlement_request = EntitlementRequest(
            meetingId=ballot.meeting_id,
            investorId=investor.investor_id,
            isin=ballot.isin,
            quantity=holding.quantity
        )

        entitlement: Entitlement | Error = await post_entitlements(
            client=client,
            base_url=base_url,
            api_key=api_key,
            entitelement_request=entitlement_request
        )
        
        error_check: None | BallotProcessingResult = error_handler(holding=entitlement)
        if error_check.isinstance(BallotProcessingResult):
             return error_check
        
        return BallotProcessingResult(
             meeting_id=ballot.meeting_id,
             success=True,
             entitlement=Entitlement
        )


    except Exception as e:
        return BallotProcessingResult(
             meeting_id=ballot.meeting_id,
             success=False,
             error=Error(
                  code="500",
                  message="Something went wrong with processing the ballots",
                  details=str(e)
             )
        )