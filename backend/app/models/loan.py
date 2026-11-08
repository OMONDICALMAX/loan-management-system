from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db


class Loan(db.Model):
    __tablename__ = "loans"

    __table_args__ = (
        db.CheckConstraint(
            "principal > 0",
            name="ck_loans_principal_positive",
        ),
        db.CheckConstraint(
            "number_of_installments > 0",
            name="ck_loans_installments_positive",
        ),
        db.CheckConstraint(
            "monthly_interest_rate >= 0",
            name="ck_loans_interest_rate_nonnegative",
        ),
        db.CheckConstraint(
            "processing_fee_rate >= 0",
            name="ck_loans_processing_fee_nonnegative",
        ),
        db.CheckConstraint(
            "transaction_cost >= 0",
            name="ck_loans_transaction_cost_nonnegative",
        ),
        db.CheckConstraint(
            "insurance_per_installment >= 0",
            name="ck_loans_insurance_nonnegative",
        ),
        db.CheckConstraint(
            "penalty_rate >= 0",
            name="ck_loans_penalty_rate_nonnegative",
        ),
        db.CheckConstraint(
            "grace_period_hours >= 0",
            name="ck_loans_grace_period_nonnegative",
        ),
        db.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', "
            "'disbursed', 'active', 'completed', 'defaulted', 'cancelled')",
            name="ck_loans_valid_status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
    )

    loan_product_id = db.Column(
        db.Integer,
        db.ForeignKey("loan_products.id"),
        nullable=False,
    )

    customer = db.relationship("Customer", backref="loans")
    loan_product = db.relationship("LoanProduct", backref="loans")

    # Loan details
    principal = db.Column(db.Numeric(12, 2), nullable=False)

    number_of_installments = db.Column(db.Integer, nullable=False)

    first_repayment_date = db.Column(db.Date, nullable=True)

    # Frozen loan terms
    monthly_interest_rate = db.Column(
        db.Numeric(5, 4),
        nullable=False,
    )

    processing_fee_rate = db.Column(
        db.Numeric(5, 4),
        nullable=False,
    )

    transaction_cost = db.Column(
        db.Numeric(12, 2),
        nullable=False,
    )

    insurance_per_installment = db.Column(
        db.Numeric(12, 2),
        nullable=False,
    )

    penalty_rate = db.Column(
        db.Numeric(5, 4),
        nullable=False,
    )

    grace_period_hours = db.Column(db.Integer, nullable=False)

    # Approval workflow
    internal_approved = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    customer_approved = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    internal_approved_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    customer_approved_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    # Loan status
    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending",
    )

    disbursed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    # Audit timestamps
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
        return f"<Loan {self.id}: {self.principal}>"