from datetime import date
from decimal import Decimal

import pytest

from app.services.loan_calculator import calculate_daily_interest


def test_daily_interest_excludes_disbursement_date():
    interest = calculate_daily_interest(
        principal=Decimal("30000.00"),
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 16),
    )

    assert interest == Decimal("3000.00")


def test_same_day_repayment_has_zero_interest():
    interest = calculate_daily_interest(
        principal=Decimal("30000.00"),
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 1),
    )

    assert interest == Decimal("0.00")


def test_interest_uses_reduced_principal():
    interest = calculate_daily_interest(
        principal=Decimal("20000.00"),
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 16),
    )

    assert interest == Decimal("2000.00")


def test_interest_uses_actual_number_of_days():
    interest = calculate_daily_interest(
        principal=Decimal("30000.00"),
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 11),
    )

    assert interest == Decimal("2000.00")


def test_negative_principal_is_rejected():
    with pytest.raises(ValueError):
        calculate_daily_interest(
            principal=Decimal("-1000.00"),
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 16),
        )


def test_end_date_before_start_date_is_rejected():
    with pytest.raises(ValueError):
        calculate_daily_interest(
            principal=Decimal("30000.00"),
            start_date=date(2026, 11, 16),
            end_date=date(2026, 11, 1),
        )


def test_negative_interest_rate_is_rejected():
    with pytest.raises(ValueError):
        calculate_daily_interest(
            principal=Decimal("30000.00"),
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 16),
            monthly_interest_rate=Decimal("-0.20"),
        )