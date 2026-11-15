from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from app import create_app
from app.extensions import db
from app.models.customer import Customer
from app.models.loan_product import LoanProduct
from app.models.loan import Loan
from app.services.loan_disbursement import record_loan_disbursement
from app.services.installment_service import create_loan_installments


app = create_app()
kenya_tz = ZoneInfo("Africa/Nairobi")

with app.app_context():
    try:
        customer = Customer(
            first_name="Test",
            last_name="Borrower",
            email="installment.test@example.com",
            phone="0700000091",
            national_id="TEST-INSTALLMENT-001",
            employer="Test Employer",
            monthly_income=Decimal("50000.00"),
            payday=15,
            employment_status="employed",
        )

        product = LoanProduct(
            name="Installment Integration Test Product",
            min_installments=1,
            max_installments=12,
        )

        db.session.add_all([customer, product])
        db.session.flush()

        loan = Loan(
            customer=customer,
            loan_product=product,
            principal=Decimal("30000.00"),
            number_of_installments=3,
            monthly_interest_rate=Decimal("0.2000"),
            processing_fee_rate=Decimal("0.0500"),
            transaction_cost=Decimal("90.00"),
            insurance_per_installment=Decimal("150.00"),
            penalty_rate=Decimal("0.3000"),
            grace_period_hours=72,
            internal_approved=True,
            customer_approved=True,
            status="approved",
        )

        db.session.add(loan)
        db.session.flush()

        disbursement_time = datetime(
            2026, 11, 8, 10, 0, tzinfo=timezone.utc
        )

        repayment_dates = record_loan_disbursement(
            loan,
            disbursement_time,
        )

        installments = create_loan_installments(
            loan,
            repayment_dates,
        )

        db.session.flush()

        assert len(installments) == 3
        assert loan.status == "disbursed"
        assert installments[0].due_date.isoformat() == "2026-11-15"
        assert installments[0].due_at.astimezone(
            kenya_tz
        ).hour == 23
        assert installments[0].due_at.astimezone(
            kenya_tz
        ).minute == 59

        assert installments[0].principal_due == Decimal("10000.00")
        assert installments[0].interest_due == Decimal("6000.00")
        assert installments[0].processing_fee == Decimal("500.00")
        assert installments[0].transaction_cost == Decimal("30.00")
        assert installments[0].insurance == Decimal("150.00")
        assert installments[0].total_due == Decimal("16680.00")

        assert installments[1].interest_due == Decimal("4000.00")
        assert installments[2].interest_due == Decimal("2000.00")
        assert installments[2].closing_principal == Decimal("0.00")

        print("Loan status:", loan.status)
        print("Repayment dates:", repayment_dates)

        for installment in installments:
            print(
                f"Installment {installment.installment_number}: "
                f"Due date={installment.due_date}, "
                f"Deadline={installment.due_at}, "
                f"Principal={installment.principal_due}, "
                f"Interest={installment.interest_due}, "
                f"Total={installment.total_due}"
            )

        print("\nSUCCESS: Installment integration test passed.")

    except Exception:
        db.session.rollback()
        raise

    finally:
        db.session.rollback()
        print("Database transaction rolled back.")
