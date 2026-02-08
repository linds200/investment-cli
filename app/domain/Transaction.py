from typing import List
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import db

class Transaction(db.Model):
    __tablename__ = 'Transaction'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String(30), ForeignKey('User.username'), nullable=False)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey('Portfolio.id'), nullable=False)
    security: Mapped[str] = mapped_column(String(10), ForeignKey('Security.ticker'), nullable=False)
    type: Mapped[str] = mapped_column(String(4), nullable=False)  # 'BUY' or 'SELL'
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[str] = mapped_column(DateTime, nullable=False)

    user_rel: Mapped["User"] = relationship('User', back_populates='transaction')
    portfolio: Mapped["Portfolio"] = relationship('Portfolio', back_populates='transaction')
    security_rel: Mapped["Security"] = relationship('Security', back_populates='transaction')