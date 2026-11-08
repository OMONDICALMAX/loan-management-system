"""add loan validation constraints

Revision ID: ae121b65daf1
Revises: b02e9bdd2beb
Create Date: 2026-11-08 20:18:28.089558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae121b65daf1'
down_revision = 'b02e9bdd2beb'
branch_labels = None
depends_on = None



def upgrade():
    op.create_check_constraint(
        "ck_loans_principal_positive",
        "loans",
        "principal > 0"
    )

    op.create_check_constraint(
        "ck_loans_installments_positive",
        "loans",
        "number_of_installments > 0"
    )

    op.create_check_constraint(
        "ck_loans_interest_rate_nonnegative",
        "loans",
        "monthly_interest_rate >= 0"
    )

    op.create_check_constraint(
        "ck_loans_processing_fee_nonnegative",
        "loans",
        "processing_fee_rate >= 0"
    )

    op.create_check_constraint(
        "ck_loans_transaction_cost_nonnegative",
        "loans",
        "transaction_cost >= 0"
    )

    op.create_check_constraint(
        "ck_loans_insurance_nonnegative",
        "loans",
        "insurance_per_installment >= 0"
    )

    op.create_check_constraint(
        "ck_loans_penalty_rate_nonnegative",
        "loans",
        "penalty_rate >= 0"
    )

    op.create_check_constraint(
        "ck_loans_grace_period_nonnegative",
        "loans",
        "grace_period_hours >= 0"
    )

    op.create_check_constraint(
        "ck_loans_valid_status",
        "loans",
        "status IN ('pending', 'approved', 'rejected', 'disbursed', 'active', 'completed', 'defaulted', 'cancelled')"
    )


def downgrade():
    op.drop_constraint(
        "ck_loans_valid_status", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_grace_period_nonnegative", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_penalty_rate_nonnegative", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_insurance_nonnegative", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_transaction_cost_nonnegative", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_processing_fee_nonnegative", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_interest_rate_nonnegative", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_installments_positive", "loans", type_="check"
    )
    op.drop_constraint(
        "ck_loans_principal_positive", "loans", type_="check"
    )

