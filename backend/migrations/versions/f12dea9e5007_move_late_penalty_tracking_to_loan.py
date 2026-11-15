
"""move late penalty tracking to loan

Revision ID: f12dea9e5007
Revises: 87e62f3cda96
"""

from alembic import op
import sqlalchemy as sa


revision = "f12dea9e5007"
down_revision = "87e62f3cda96"
branch_labels = None
depends_on = None


def upgrade():
    # Remove the old installment-level penalty constraint and fields.
    with op.batch_alter_table("loan_installments") as batch_op:
        batch_op.drop_constraint(
            "ck_installments_penalty_nonnegative",
            type_="check",
        )
        batch_op.drop_column("penalty_applied_at")
        batch_op.drop_column("penalty_amount")

    # Add penalty tracking to loans.
    with op.batch_alter_table("loans") as batch_op:
        batch_op.add_column(
            sa.Column(
                "penalty_amount",
                sa.Numeric(12, 2),
                nullable=False,
                server_default=sa.text("0.00"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "penalty_applied_at",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )
        batch_op.create_check_constraint(
            "ck_loans_penalty_amount_nonnegative",
            "penalty_amount >= 0",
        )
        batch_op.alter_column(
            "penalty_amount",
            server_default=None,
        )


def downgrade():
    # Remove loan-level penalty tracking.
    with op.batch_alter_table("loans") as batch_op:
        batch_op.drop_constraint(
            "ck_loans_penalty_amount_nonnegative",
            type_="check",
        )
        batch_op.drop_column("penalty_applied_at")
        batch_op.drop_column("penalty_amount")

    # Restore installment-level penalty fields.
    with op.batch_alter_table("loan_installments") as batch_op:
        batch_op.add_column(
            sa.Column(
                "penalty_amount",
                sa.Numeric(12, 2),
                nullable=False,
                server_default=sa.text("0.00"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "penalty_applied_at",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )
        batch_op.create_check_constraint(
            "ck_installments_penalty_nonnegative",
            "penalty_amount >= 0",
        )
        batch_op.alter_column(
            "penalty_amount",
            server_default=None,
        )
