
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.services.repayment_schedule import generate_repayment_dates


KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


def record_loan_disbursement(loan, disbursed_at):
    """
    Record a successfully completed loan disbursement.

    The repayment dates are calculated using the customer's
    payday and the Kenya calendar date of disbursement.

    This function updates the loan in the current database
    session but does not commit the transaction.
    """

    if loan.status != "approved":
        raise ValueError("Only approved loans can be disbursed.")

    if not loan.internal_approved or not loan.customer_approved:
        raise ValueError(
            "Both internal and customer approval are required."
        )

    if loan.disbursed_at is not None:
        raise ValueError("This loan has already been disbursed.")

    if loan.first_repayment_date is not None:
        raise ValueError(
            "The first repayment date has already been set."
        )

    if not isinstance(disbursed_at, datetime):
        raise ValueError("Disbursement timestamp must be a datetime.")

    if (
        disbursed_at.tzinfo is None
        or disbursed_at.utcoffset() is None
    ):
        raise ValueError(
            "Disbursement timestamp must include timezone information."
        )

    customer = loan.customer

    if customer is None:
        raise ValueError("The loan has no associated customer.")

    if customer.employment_status.strip().lower() != "employed":
        raise ValueError("Only employed customers can receive loans.")

    payday = customer.payday

    repayment_dates = generate_repayment_dates(
        disbursement_date=disbursed_at.astimezone(
            KENYA_TIMEZONE
        ).date(),
        payday=payday,
        number_of_installments=loan.number_of_installments,
    )

    loan.disbursed_at = disbursed_at.astimezone(timezone.utc)
    loan.first_repayment_date = repayment_dates[0]
    loan.status = "disbursed"

    return repayment_dates
