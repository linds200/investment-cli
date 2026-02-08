from datetime import datetime, timezone
from typing import List
from rich.console import Console
from rich.table import Table
from app.db import db
from app.domain import User, Investment, Portfolio, Security, Transaction

_console = Console()

class UnsupportedSecurityOperation(Exception):
    pass

def get_all_securities() -> List[Security]:
    session = None
    try:
        session = db.session
        securities = session.query(Security).all()
        if not securities:
            raise UnsupportedSecurityOperation("No securities found.")
        return securities
    finally:
        session.close() if session else None

def print_all_securities(securities: List[Security]):
    table = Table(title = "Available Securities")
    table.add_column("Ticker", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("Issuer", style = "magenta")
    table.add_column("Reference Price", justify = "right", style = "green")
    for security in securities:
        table.add_row(security.ticker, security.issuer, f"${security.price:.2f}")
    _console.print(table)

def place_buy_order(logged_in_user: str, portfolio_id: int, ticker: str, quantity_input: int) -> str:
    session = None
    try:
        session = db.session
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise UnsupportedSecurityOperation(f"Portfolio with ID {portfolio_id} does not exist.")
        security = session.query(Security).filter(Security.ticker == ticker).first()
        if not security:
            raise UnsupportedSecurityOperation(f"Security with ticker {ticker} does not exist.")
        if portfolio.owner_username != logged_in_user:
            raise UnsupportedSecurityOperation("You do not have permission to place a buy order for this portfolio.")
        total_cost = security.price * quantity_input
        user = session.query(User).filter_by(username = logged_in_user).first()
        if total_cost > user.balance:
            raise UnsupportedSecurityOperation("Insufficient balance to place buy order.")
        
        user.balance -= total_cost
        investment = (session.query(Investment).filter_by(portfolio_id = portfolio.id, ticker = ticker).first())
        if investment:
            # Add quantity to existing holding
            investment.quantity += quantity_input
        else:
            # Create new investment position
            investment = Investment(portfolio_id = portfolio.id, ticker = ticker, quantity = quantity_input)
            session.add(investment)

        # use UTC timestamp
        session.add(Transaction(user = user.username, portfolio_id = portfolio.id, security = ticker, type = 'BUY', quantity = quantity_input, price = security.price, timestamp = datetime.now(timezone.utc)))
        session.commit()
    finally:
        session.close() if session else None