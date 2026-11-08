
from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db


class LoanProduct(db.Model):
    __tablename__ = "loan_products"

    
    __table_args__ = (
        db.CheckConstraint(
            "min_installments IS NULL OR min_installments > 0",
            name="ck_loan_products_min_installments_positive",
        ),
        db.CheckConstraint(
            "max_installments IS NULL OR max_installments > 0",
            name="ck_loan_products_max_installments_positive",
        ),
        db.CheckConstraint(
            """
            min_installments IS NULL
            OR max_installments IS NULL
            OR max_installments >= min_installments
            """,
            name="ck_loan_products_valid_installment_range",
        ),
    )


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

    
    # Permitted repayment period
    min_installments = db.Column(
        db.Integer,
        nullable=True,
    )

    max_installments = db.Column(
        db.Integer,
        nullable=True,
    )


    def __repr__(self):
        return f"<LoanProduct {self.name}>"
