from typing import List
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.domain import Investment, Transaction, User
class Portfolio(Base):
    __tablename__ = 'Portfolio'
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    owner_username: Mapped[str] = mapped_column(String(30), ForeignKey('User.username'), nullable = False)
    name: Mapped[str] = mapped_column(String(50), nullable = False)
    description: Mapped[str] = mapped_column(String(500), nullable = True)
    investment_strategy: Mapped[str] = mapped_column(String(100), nullable = True)
    
    user: Mapped[List[User]] = relationship('User', back_populates = 'portfolio')
    investment: Mapped[List[Investment]] = relationship('Investment', back_populates = 'portfolio')
    transaction: Mapped[List[Transaction]] = relationship('Transaction', back_populates = 'portfolio')