from datetime import datetime, timezone
from typing import List
from rich.console import Console
from rich.table import Table
from app import database
from app.domain.Investment import Investment
from app.domain.Portfolio import Portfolio
from app.domain.Transaction import Transaction
from app.domain.User import User
from app.services.login_service import get_logged_in_user

_console = Console()

def get_all_portfolios() -> List[Portfolio]:
    session = None
    try:
        user = get_logged_in_user()
        session = database.get_session()
        portfolios = (session.query(Portfolio).filter_by(owner_username = user.username).all())
        if not portfolios:
            _console.print("\nNo portfolios found for the logged-in user.\n", style = "bold yellow")
        return portfolios
    finally:
        if session:
            session.close()

def print_all_portfolios(portfolios: List[Portfolio]):
    table = Table(title = "Portfolios")
    table.add_column("ID", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("Owner", style = "magenta")
    table.add_column("Name", style = "magenta")
    table.add_column("Description", style = "magenta")
    table.add_column("Investment Strategy", style = "magenta")
    for portfolio in portfolios:
        table.add_row(str(portfolio.id), portfolio.owner_username, portfolio.name, portfolio.description, portfolio.investment_strategy)
    _console.print(table)

def create_portfolio() -> str:
    session = None
    try:
        name = _console.input("Enter Portfolio Name: ")
        description = _console.input("Enter Portfolio Description: ")
        investment_strategy = _console.input("Enter Investment Strategy: ")
        owner_username = get_logged_in_user().username
        session = database.get_session()
        session.add(Portfolio(owner_username = owner_username, name = name, description = description, investment_strategy = investment_strategy))
        session.commit()
        _console.print(f"\nPortfolio {name} created successfully.\n", style = "bold green")
    except ValueError:
        _console.print("\nInvalid input. Please try again.\n", style = "bold red")
    finally:
        session.close() if session else None

def delete_portfolio() -> str:
    session = None
    try:
        portfolio_id = int(_console.input("Enter Portfolio ID to delete: "))
        session = database.get_session()
        portfolio = session.query(Portfolio).filter_by(id = portfolio_id).first()
        if portfolio is None:
            _console.print(f"\nPortfolio with ID {portfolio_id} does not exist.\n", style = "bold red")
            return
        user = get_logged_in_user()
        if portfolio.owner_username != user.username:
            _console.print("\nYou do not have permission to delete this portfolio.\n", style = "bold red")
            return
        if portfolio.investment:
            _console.print("\nCannot delete a portfolio that has investments. Please harvest all investments first.\n", style = "bold red")
            return
        session.delete(portfolio)
        session.commit()
        _console.print(f"\nPortfolio with ID {portfolio_id} deleted successfully.\n", style = "bold green")
    except ValueError:
        _console.print("\nInvalid input. Portfolio ID must be a number.\n", style = "bold red")
    except Exception as e:
        # Generic safety net so SQL errors or unexpected issues are caught
        _console.print(f"\nUnexpected error: {e}\n", style = "bold red")
    finally:
        session.close() if session else None

def harvest_investment() -> str:
    session = None
    try:
        portfolio_id = int(_console.input("Enter Portfolio ID to harvest from: "))
        ticker = _console.input("Enter Ticker of Investment to harvest: ")
        quantity_input = int(_console.input("Enter Quantity to harvest: "))
        sale_price = float(_console.input("Enter Sale Price per Unit: "))
        
        session = database.get_session()
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            _console.print(f"\nPortfolio with ID {portfolio_id} does not exist.\n", style = "bold red")
            return
        logged_in = get_logged_in_user()
        user = session.query(User).filter_by(username=logged_in.username).first()
        if portfolio.owner_username != user.username:
            _console.print("\nYou do not have permission to harvest from this portfolio.\n", style = "bold red")
            return
        portfolio_investment = session.query(Investment).filter(Investment.portfolio_id == portfolio.id, Investment.ticker == ticker).first()
        if not portfolio_investment:
            _console.print(f"\nNo investment with ticker {ticker} found in Portfolio {portfolio.id}.\n", style = "bold red")
            return
        if quantity_input > portfolio_investment.quantity:
            _console.print("\nInsufficient quantity of investment to harvest.\n", style = "bold red")
            return
        user.balance += quantity_input * sale_price
        portfolio_investment.quantity -= quantity_input
        if portfolio_investment.quantity == 0:
            session.delete(portfolio_investment)
        session.add(Transaction(user = user.username, portfolio_id = portfolio.id, security = ticker, type = 'SELL', quantity = quantity_input, price = sale_price, timestamp = datetime.now(timezone.utc)))
        session.commit()
        _console.print(f"\nHarvested {quantity_input} shares of {ticker} from Portfolio {portfolio.id}.\n", style = "bold green")
    finally:
        session.close() if session else None