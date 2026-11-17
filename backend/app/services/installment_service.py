
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from app.models.loan_installment import LoanInstallment
from app.services.loan_calculator import calculate_repayment_schedule


KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")


def create_loan_installments(loan, repayment_dates):
    """
    Generate and attach installment records to a disbursed loan.

    Uses the loan's frozen financial terms and the repayment
    dates calculated during disbursement.

    This function does not commit the database transaction.
    """

    if loan.status != "disbursed":
        raise ValueError("Only disbursed loans can have installments.")

    if loan.disbursed_at is None:
        raise ValueError("The loan has no disbursement timestamp.")

    if loan.first_repayment_date is None:
        raise ValueError("The first repayment date has not been set.")

    if loan.installments:
        raise ValueError("Installments have already been created.")

    if not isinstance(repayment_dates, (list, tuple)):
        raise ValueError("Repayment dates must be a list or tuple.")

    if len(repayment_dates) != loan.number_of_installments:
        raise ValueError(
            "The number of repayment dates must match "
            "the number of loan installments."
        )

    for index, repayment_date in enumerate(repayment_dates):
        if (
            isinstance(repayment_date, datetime)
            or not isinstance(repayment_date, date)
        ):
            raise ValueError("Every repayment date must be a date.")

        if index > 0 and repayment_date <= repayment_dates[index - 1]:
            raise ValueError(
                "Repayment dates must be in strictly increasing order."
            )

    if repayment_dates[0] != loan.first_repayment_date:
        raise ValueError(
            "The first repayment date does not match the loan record."
        )

    schedule = calculate_repayment_schedule(
        principal=loan.principal,
        number_of_installments=loan.number_of_installments,
        monthly_interest_rate=loan.monthly_interest_rate,
        processing_fee_rate=loan.processing_fee_rate,
        transaction_cost=loan.transaction_cost,
        insurance_per_installment=loan.insurance_per_installment,
    )

    installments = []

    for item, repayment_date in zip(schedule, repayment_dates):
        due_at = datetime.combine(
            repayment_date,
            time(23, 59),
            tzinfo=KENYA_TIMEZONE,
        )

        installment = LoanInstallment(
            installment_number=item["installment_number"],
            due_date=repayment_date,
            due_at=due_at,
            opening_principal=item["opening_principal"],
            principal_due=item["principal"],
            interest_due=item["interest"],
            processing_fee=item["processing_fee"],
            transaction_cost=item["transaction_cost"],
            insurance=item["insurance"],
            total_due=item["total_due"],
            closing_principal=item["closing_principal"],
            amount_paid=0,
            status="pending",
        )

        installments.append(installment)

    loan.installments.extend(installments)

    return installments
