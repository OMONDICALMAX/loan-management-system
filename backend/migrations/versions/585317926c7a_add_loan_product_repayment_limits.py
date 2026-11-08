"""add loan product repayment limits

Revision ID: 585317926c7a
Revises: ae121b65daf1
Create Date: 2026-11-08 21:31:34.970617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '585317926c7a'
down_revision = 'ae121b65daf1'
branch_labels = None
depends_on = None



def upgrade():
    with op.batch_alter_table('loan_products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('min_installments', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('max_installments', sa.Integer(), nullable=True))

        batch_op.create_check_constraint(
            'ck_loan_products_min_installments_positive',
            'min_installments IS NULL OR min_installments > 0'
        )

        batch_op.create_check_constraint(
            'ck_loan_products_max_installments_positive',
            'max_installments IS NULL OR max_installments > 0'
        )

        batch_op.create_check_constraint(
            'ck_loan_products_valid_installment_range',
            'min_installments IS NULL OR max_installments IS NULL OR max_installments >= min_installments'
        )


def downgrade():
    with op.batch_alter_table('loan_products', schema=None) as batch_op:
        batch_op.drop_constraint(
            'ck_loan_products_valid_installment_range',
            type_='check'
        )
        batch_op.drop_constraint(
            'ck_loan_products_max_installments_positive',
            type_='check'
        )
        batch_op.drop_constraint(
            'ck_loan_products_min_installments_positive',
            type_='check'
        )

        batch_op.drop_column('max_installments')
        batch_op.drop_column('min_installments')
