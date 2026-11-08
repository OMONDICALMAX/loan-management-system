
import calendar
from datetime import date, datetime


def generate_repayment_dates(
    disbursement_date,
    payday,
    number_of_installments,
):
    """
    Generate monthly repayment dates based on the customer's payday.

    The first repayment date is the next payday strictly after
    the disbursement date.

    If a month does not contain the requested payday, its final
    calendar day is used.
    """

    if isinstance(disbursement_date, datetime) or not isinstance(
        disbursement_date, date
    ):
        raise ValueError("Disbursement date must be a date.")

    if (
        isinstance(payday, bool)
        or not isinstance(payday, int)
        or not 1 <= payday <= 31
    ):
        raise ValueError("Payday must be an integer between 1 and 31.")

    if (
        isinstance(number_of_installments, bool)
        or not isinstance(number_of_installments, int)
        or number_of_installments <= 0
    ):
        raise ValueError("Number of installments must be a positive integer.")

    repayment_dates = []

    year = disbursement_date.year
    month = disbursement_date.month

    while len(repayment_dates) < number_of_installments:
        days_in_month = calendar.monthrange(year, month)[1]
        repayment_day = min(payday, days_in_month)

        repayment_date = date(year, month, repayment_day)

        if repayment_date > disbursement_date:
            repayment_dates.append(repayment_date)

        # Move to the next calendar month.
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    return repayment_dates
