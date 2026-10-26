
from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db


class LoanProduct(db.Model):
    __tablename__ = "loan_products"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    # Interest and fee settings
    monthly_interest_rate = db.Column(
        db.Numeric(5, 4),
        nullable=False,
        default=Decimal("0.2000"),
    )

    processing_fee_rate = db.Column(
        db.Numeric(5, 4),
        nullable=False,
        default=Decimal("0.0500"),
    )

    transaction_cost = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("90.00"),
    )

    insurance_per_installment = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("150.00"),
    )

    # Repayment and penalty settings
    repayment_frequency = db.Column(
        db.String(20),
        nullable=False,
        default="monthly",
    )

    grace_period_hours = db.Column(
        db.Integer,
        nullable=False,
        default=72,
    )

    penalty_rate = db.Column(
        db.Numeric(5, 4),
        nullable=False,
        default=Decimal("0.3000"),
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<LoanProduct {self.name}>"
