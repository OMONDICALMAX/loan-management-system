from datetime import datetime, timezone

from app.extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    national_id = db.Column(db.String(50), nullable=False, unique=True)

    employer = db.Column(db.String(255), nullable=False)
    monthly_income = db.Column(db.Numeric(12, 2), nullable=False)

    payday = db.Column(db.Integer, nullable=False)

    employment_status = db.Column(
        db.String(50),
        nullable=False,
        default="employed",
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
        return f"<Customer {self.first_name} {self.last_name}>"
