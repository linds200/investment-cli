from typing import List
from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.domain import Portfolio, Transaction

class User (Base):
    __tablename__ = 'User'
    username: Mapped[str] = mapped_column(String (30), primary_key = True)
    password: Mapped[str] = mapped_column(String(30), nullable = False)
    firstname: Mapped[str] = mapped_column(String(30), nullable = False)
    lastname: Mapped[str] = mapped_column(String(30), nullable = False)
    balance: Mapped[float] = mapped_column(Float, nullable = False)
    
    portfolio: Mapped[List[Portfolio]] = relationship('Portfolio', back_populates = 'user')
    transaction: Mapped[List[Transaction]] = relationship('Transaction', back_populates = 'user_rel')
        
    def __str__(self):
        return f"User: username = {self.username}; name = {self.firstname} {self.lastname}, balance = {self.balance}"