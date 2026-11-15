
from datetime import datetime, timezone

from app.extensions import db


class LoanInstallment(db.Model):
    __tablename__ = "loan_installments"

    __table_args__ = (
        db.UniqueConstraint(
            "loan_id",
            "installment_number",
            name="uq_loan_installment_number",
        ),
        db.CheckConstraint(
            "installment_number > 0",
            name="ck_installments_number_positive",
        ),
        db.CheckConstraint(
            "total_due >= 0 AND amount_paid >= 0",
            name="ck_installments_amounts_nonnegative",
        ),
        db.CheckConstraint(
            "status IN ('pending', 'partially_paid', 'paid', 'overdue')",
            name="ck_installments_valid_status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    loan_id = db.Column(
        db.Integer,
        db.ForeignKey("loans.id"),
        nullable=False,
    )

    loan = db.relationship(
        "Loan",
        back_populates="installments",
    )

    installment_number = db.Column(db.Integer, nullable=False)

    due_date = db.Column(db.Date, nullable=False)

    # Exact repayment deadline in Kenya time.
    due_at = db.Column(db.DateTime(timezone=True), nullable=False)

    opening_principal = db.Column(db.Numeric(12, 2), nullable=False)
    principal_due = db.Column(db.Numeric(12, 2), nullable=False)
    interest_due = db.Column(db.Numeric(12, 2), nullable=False)
    processing_fee = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_cost = db.Column(db.Numeric(12, 2), nullable=False)
    insurance = db.Column(db.Numeric(12, 2), nullable=False)
    total_due = db.Column(db.Numeric(12, 2), nullable=False)
    closing_principal = db.Column(db.Numeric(12, 2), nullable=False)

    amount_paid = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0,
    )

    paid_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending",
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
        return (
            f"<LoanInstallment {self.installment_number} "
            f"for Loan {self.loan_id}>"
        )
