from datetime import datetime, timezone
from typing import List
from rich.console import Console
from rich.table import Table
from app import database
from app.domain.Investment import Investment
from app.domain.Portfolio import Portfolio
from app.domain.Security import Security
from app.domain.Transaction import Transaction
from app.services.login_service import get_logged_in_user


_console = Console()

def get_all_securities() -> List[Security]:
    try: 
        session = database.get_session()
        securities = session.query(Security).all()
    finally:
        session.close()
    return securities

def print_all_securities(securities: List[Security]):
    table = Table(title = "Available Securities")
    table.add_column("Ticker", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("Issuer", style = "magenta")
    table.add_column("Reference Price", justify = "right", style = "green")
    for security in securities:
        table.add_row(security.ticker, security.issuer, f"${security.price:.2f}")
    _console.print(table)

def place_buy_order() -> str:
    session = None
    try:
        portfolio_id = int(_console.input("Enter Portfolio ID to use for Purchase: "))
        ticker = _console.input("Enter Ticker of Security to Buy: ")
        quantity_input = int(_console.input("Enter Quantity to Buy: "))
        
        session = database.get_session()
        security = session.query(Security).filter(Security.ticker == ticker).first()
        if not security:
            _console.print(f"\nSecurity with ticker '{ticker}' does not exist.\n", style="bold red")
            return
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            _console.print(f"\nPortfolio with ID {portfolio_id} does not exist.\n", style="bold red")
            return
        user = get_logged_in_user()
        if portfolio.owner_username != user.username:
            _console.print("\nYou do not have permission to place a buy order for this portfolio.\n", style="bold red")
            return
        total_cost = security.price * quantity_input
        if total_cost > user.balance:
            _console.print("\nInsufficient balance to place buy order.\n", style="bold red")
            return
        
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
        _console.print(f"\nPlaced buy order for {quantity_input} shares of {ticker}.\n", style = "bold green")
    finally:
        session.close() if session else None