from typing import List
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.db import db

class Investment(db.Model):
    __tablename__ = 'Investment'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey('Portfolio.id'), nullable=False)
    ticker: Mapped[str] = mapped_column(String(10), ForeignKey('Security.ticker'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    security: Mapped["Security"] = relationship('Security', back_populates='investment')
    portfolio: Mapped["Portfolio"] = relationship('Portfolio', back_populates='investment')

    def total_value(self) -> float:
        return self.quantity * self.security.price