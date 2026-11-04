from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.services.loan_calculator import (
    calculate_late_penalty,
    calculate_repayment_schedule,
)

ZERO = Decimal("0.00")
DUE_AT = datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc)


def total(schedule, key):
    return sum((row[key] for row in schedule), ZERO)


# ---------- Late penalty ----------

def test_late_penalty_uses_remaining_principal_only():
    penalty = calculate_late_penalty(
        remaining_principal=Decimal("20000.00"),
        due_at=DUE_AT,
        now=DUE_AT + timedelta(hours=72),
    )

    assert penalty == Decimal("6000.00")


def test_zero_remaining_principal_has_no_penalty():
    penalty = calculate_late_penalty(
        remaining_principal=Decimal("0.00"),
        due_at=DUE_AT,
        now=DUE_AT + timedelta(hours=72),
    )

    assert penalty == ZERO


def test_custom_penalty_rate():
    penalty = calculate_late_penalty(
        remaining_principal=Decimal("10000.00"),
        due_at=DUE_AT,
        now=DUE_AT + timedelta(hours=72),
        penalty_rate=Decimal("0.10"),
    )

    assert penalty == Decimal("1000.00")


def test_negative_remaining_principal_is_rejected():
    with pytest.raises(ValueError):
        calculate_late_penalty(
            remaining_principal=Decimal("-1.00"),
            due_at=DUE_AT,
            now=DUE_AT + timedelta(hours=72),
        )


def test_negative_penalty_rate_is_rejected():
    with pytest.raises(ValueError):
        calculate_late_penalty(
            remaining_principal=Decimal("1000.00"),
            due_at=DUE_AT,
            now=DUE_AT + timedelta(hours=72),
            penalty_rate=Decimal("-0.01"),
        )


# ---------- Repayment schedule ----------

def test_principal_is_fully_repaid():
    schedule = calculate_repayment_schedule(
        principal=Decimal("30000.00"),
        number_of_installments=3,
    )

    assert total(schedule, "principal") == Decimal("30000.00")
    assert schedule[-1]["closing_principal"] == ZERO


def test_fees_and_insurance_are_separate():
    schedule = calculate_repayment_schedule(
        principal=Decimal("30000.00"),
        number_of_installments=3,
    )

    assert total(schedule, "processing_fee") == Decimal("1500.00")
    assert total(schedule, "transaction_cost") == Decimal("90.00")
    assert total(schedule, "insurance") == Decimal("450.00")


def test_interest_and_payments_decrease():
    schedule = calculate_repayment_schedule(
        principal=Decimal("30000.00"),
        number_of_installments=3,
    )

    assert schedule[0]["interest"] > schedule[1]["interest"]
    assert schedule[1]["interest"] > schedule[2]["interest"]

    assert schedule[0]["total_due"] > schedule[1]["total_due"]
    assert schedule[1]["total_due"] > schedule[2]["total_due"]


@pytest.mark.parametrize(
    "principal, installments",
    [
        ("0.00", 3),
        ("-1000.00", 3),
        ("1000.00", 0),
        ("1000.00", -1),
    ],
)
def test_invalid_loan_inputs_are_rejected(principal, installments):
    with pytest.raises(ValueError):
        calculate_repayment_schedule(
            principal=Decimal(principal),
            number_of_installments=installments,
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"monthly_interest_rate": Decimal("-0.01")},
        {"processing_fee_rate": Decimal("-0.01")},
        {"transaction_cost": Decimal("-1.00")},
        {"insurance_per_installment": Decimal("-1.00")},
    ],
)
def test_negative_schedule_rates_or_fees_are_rejected(kwargs):
    with pytest.raises(ValueError):
        calculate_repayment_schedule(
            principal=Decimal("1000.00"),
            number_of_installments=3,
            **kwargs,
        )


# ---------- Rounding ----------

def test_rounding_reconciles_principal_exactly():
    schedule = calculate_repayment_schedule(
        principal=Decimal("1000.00"),
        number_of_installments=3,
    )

    principal_parts = [row["principal"] for row in schedule]

    assert principal_parts == [
        Decimal("333.33"),
        Decimal("333.33"),
        Decimal("333.34"),
    ]
    assert sum(principal_parts, ZERO) == Decimal("1000.00")
    assert schedule[-1]["closing_principal"] == ZERO


def test_rounding_reconciles_processing_fee_exactly():
    schedule = calculate_repayment_schedule(
        principal=Decimal("101.00"),
        number_of_installments=3,
    )

    processing_fees = [row["processing_fee"] for row in schedule]

    assert processing_fees == [
        Decimal("1.68"),
        Decimal("1.68"),
        Decimal("1.69"),
    ]
    assert sum(processing_fees, ZERO) == Decimal("5.05")


def test_rounding_reconciles_transaction_cost_exactly():
    schedule = calculate_repayment_schedule(
        principal=Decimal("1000.00"),
        number_of_installments=7,
    )

    assert total(schedule, "transaction_cost") == Decimal("90.00")

def test_no_penalty_before_72_hour_grace_period():
    penalty = calculate_late_penalty(
        remaining_principal=Decimal("20000.00"),
        due_at=DUE_AT,
        now=DUE_AT + timedelta(hours=71, minutes=59),
    )

    assert penalty == ZERO


def test_penalty_applies_at_exactly_72_hours():
    penalty = calculate_late_penalty(
        remaining_principal=Decimal("20000.00"),
        due_at=DUE_AT,
        now=DUE_AT + timedelta(hours=72),
    )

    assert penalty == Decimal("6000.00")


def test_penalty_remains_same_after_72_hours():
    penalty = calculate_late_penalty(
        remaining_principal=Decimal("20000.00"),
        due_at=DUE_AT,
        now=DUE_AT + timedelta(hours=96),
    )

    assert penalty == Decimal("6000.00")


def test_already_applied_penalty_is_not_charged_again():
    penalty = calculate_late_penalty(
        remaining_principal=Decimal("20000.00"),
        due_at=DUE_AT,
        now=DUE_AT + timedelta(hours=96),
        penalty_already_applied=True,
    )

    assert penalty == ZERO

def test_naive_due_date_is_rejected():
    due_at = datetime(2026, 10, 1, 9, 0)

    with pytest.raises(ValueError):
        calculate_late_penalty(
            remaining_principal=Decimal("20000.00"),
            due_at=due_at,
            now=DUE_AT + timedelta(hours=72),
        )


def test_naive_current_time_is_rejected():
    with pytest.raises(ValueError):
        calculate_late_penalty(
            remaining_principal=Decimal("20000.00"),
            due_at=DUE_AT,
            now=datetime(2026, 10, 4, 9, 0),
        )


def test_negative_grace_period_is_rejected():
    with pytest.raises(ValueError):
        calculate_late_penalty(
            remaining_principal=Decimal("20000.00"),
            due_at=DUE_AT,
            now=DUE_AT + timedelta(hours=72),
            grace_period_hours=-1,
        )


def test_boolean_grace_period_is_rejected():
    with pytest.raises(ValueError):
        calculate_late_penalty(
            remaining_principal=Decimal("20000.00"),
            due_at=DUE_AT,
            now=DUE_AT + timedelta(hours=72),
            grace_period_hours=True,
        )