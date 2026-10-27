
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, timezone


CENT = Decimal("0.01")

DEFAULT_MONTHLY_INTEREST_RATE = Decimal("0.20")
DEFAULT_PROCESSING_FEE_RATE = Decimal("0.05")
DEFAULT_TRANSACTION_COST = Decimal("90.00")
DEFAULT_INSURANCE_PER_INSTALLMENT = Decimal("150.00")
DEFAULT_PENALTY_RATE = Decimal("0.30")
DEFAULT_GRACE_PERIOD_HOURS = 72


def to_decimal(value):
    """Convert numeric input to Decimal without introducing float errors."""
    return Decimal(str(value))


def money(value):
    """Round a monetary amount to two decimal places."""
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def split_amount(total, number_of_installments):
    """Split a total amount evenly and reconcile rounding in the final installment."""
    total = money(total)
    regular_amount = money(total / number_of_installments)

    amounts = [regular_amount] * (number_of_installments - 1)
    amounts.append(money(total - sum(amounts, Decimal("0.00"))))

    return amounts


def calculate_repayment_schedule(
    principal,
    number_of_installments,
    monthly_interest_rate=DEFAULT_MONTHLY_INTEREST_RATE,
    processing_fee_rate=DEFAULT_PROCESSING_FEE_RATE,
    transaction_cost=DEFAULT_TRANSACTION_COST,
    insurance_per_installment=DEFAULT_INSURANCE_PER_INSTALLMENT,
):
    """
    Calculate a reducing-balance repayment schedule with equal principal.

    Interest is charged on opening principal.
    Fees and insurance are listed separately from principal and interest.
    """

    principal = money(principal)
    monthly_interest_rate = to_decimal(monthly_interest_rate)
    processing_fee_rate = to_decimal(processing_fee_rate)
    transaction_cost = money(transaction_cost)
    insurance_per_installment = money(insurance_per_installment)

    if principal <= 0:
        raise ValueError("Principal must be greater than zero.")

    if (
        isinstance(number_of_installments, bool)
        or not isinstance(number_of_installments, int)
        or number_of_installments <= 0
    ):
        raise ValueError("Number of installments must be a positive integer.")

    if monthly_interest_rate < 0 or processing_fee_rate < 0:
        raise ValueError("Interest and processing fee rates cannot be negative.")

    if transaction_cost < 0 or insurance_per_installment < 0:
        raise ValueError("Transaction cost and insurance cannot be negative.")

    principal_parts = split_amount(principal, number_of_installments)

    total_processing_fee = money(principal * processing_fee_rate)
    processing_parts = split_amount(
        total_processing_fee, number_of_installments
    )
    transaction_parts = split_amount(
        transaction_cost, number_of_installments
    )

    schedule = []
    outstanding_principal = principal

    for index in range(number_of_installments):
        opening_principal = outstanding_principal
        principal_payment = principal_parts[index]

        interest = money(opening_principal * monthly_interest_rate)

        processing_fee = processing_parts[index]
        installment_transaction_cost = transaction_parts[index]
        insurance = insurance_per_installment

        total_due = money(
            principal_payment
            + interest
            + processing_fee
            + installment_transaction_cost
            + insurance
        )

        outstanding_principal = money(
            opening_principal - principal_payment
        )

        schedule.append(
            {
                "installment_number": index + 1,
                "opening_principal": opening_principal,
                "principal": principal_payment,
                "interest": interest,
                "processing_fee": processing_fee,
                "transaction_cost": installment_transaction_cost,
                "insurance": insurance,
                "total_due": total_due,
                "closing_principal": outstanding_principal,
            }
        )

    return schedule



def calculate_late_penalty(
    remaining_principal,
    due_at,
    now=None,
    penalty_already_applied=False,
    penalty_rate=DEFAULT_PENALTY_RATE,
    grace_period_hours=DEFAULT_GRACE_PERIOD_HOURS,
):
    """
    Calculate a one-time penalty for an overdue installment.

    The penalty becomes eligible after the grace period has elapsed.
    The penalty is based only on remaining principal.

    This function does not update principal or persist penalty records.
    """

    remaining_principal = money(remaining_principal)
    penalty_rate = to_decimal(penalty_rate)

    if remaining_principal < 0:
        raise ValueError("Remaining principal cannot be negative.")

    if penalty_rate < 0:
        raise ValueError("Penalty rate cannot be negative.")

    if (
        isinstance(grace_period_hours, bool)
        or not isinstance(grace_period_hours, int)
        or grace_period_hours < 0
    ):
        raise ValueError("Grace period must be a non-negative integer.")

    if penalty_already_applied:
        return Decimal("0.00")

    if remaining_principal == 0:
        return Decimal("0.00")

    if not isinstance(due_at, datetime):
        raise ValueError("Due date must be a datetime.")

    if due_at.tzinfo is None or due_at.utcoffset() is None:
        raise ValueError("Due date must include a timezone.")

    if now is None:
        now = datetime.now(timezone.utc)

    if not isinstance(now, datetime):
        raise ValueError("Current time must be a datetime.")

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Current time must include a timezone.")

    grace_period_ends_at = due_at + timedelta(
        hours=grace_period_hours
    )

    if now < grace_period_ends_at:
        return Decimal("0.00")

    return money(remaining_principal * penalty_rate)
