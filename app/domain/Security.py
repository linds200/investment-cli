from typing import List
from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.domain import Investment, Transaction
class Security (Base):
    __tablename__ = 'Security'
    ticker: Mapped[str] = mapped_column(String(10), primary_key = True)
    issuer: Mapped[str] = mapped_column(String(100), nullable = False)
    price: Mapped[float] = mapped_column(Float, nullable = False)

    investment: Mapped[List[Investment]] = relationship('Investment', back_populates = 'security')
    transaction: Mapped[List[Transaction]] = relationship('Transaction', back_populates = 'security_rel')
