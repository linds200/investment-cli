from datetime import datetime, timezone
from typing import List
from rich.console import Console
from rich.table import Table
from app.db import db
from app.domain import Investment, Portfolio, Transaction, User, Security

_console = Console()
class UnsupportedPortfolioOperation(Exception):
    pass

def get_all_portfolios() -> List[Portfolio]:
    session = None
    try:
        session = db.session
        portfolios = session.query(Portfolio).all()
        if not portfolios:
            raise UnsupportedPortfolioOperation("No portfolios found.")
        return portfolios
    finally:
        session.close() if session else None

def get_all_portfolios_by_user(user: str) -> List[Portfolio]:
    session = None
    try:
        session = db.session
        portfolios = (session.query(Portfolio).filter_by(owner_username = user).all())
        if not portfolios:
            raise UnsupportedPortfolioOperation(f"No portfolios found for user {user}.")
        return portfolios
    finally:
        session.close() if session else None

def get_portfolio_by_id(portfolio_id: int) -> Portfolio:
    session = None
    try:
        session = db.session
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise UnsupportedPortfolioOperation(f"Portfolio with ID {portfolio_id} does not exist.")
        return portfolio
    finally:
        session.close() if session else None

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

def get_all_transactions(logged_in_user: str, portfolio_id: int, security: str) -> List[Transaction]:
    session = None
    try:
        session = db.session
        if portfolio_id == "all":
            portfolios = session.query(Portfolio).filter(Portfolio.owner_username == logged_in_user).all()
            if not portfolios:
                raise UnsupportedPortfolioOperation(f"No portfolios found for user {logged_in_user}.")
            portfolio_ids = [portfolio.id for portfolio in portfolios]
            transactions = session.query(Transaction).filter(Transaction.portfolio_id.in_(portfolio_ids)).all()
            if not transactions:
                raise UnsupportedPortfolioOperation(f"No transactions found for user {logged_in_user}.")
        else:
            portfolio_id = int(portfolio_id)
            if not isinstance(portfolio_id, int):
                raise UnsupportedPortfolioOperation("Portfolio ID must be an integer.")
            portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                raise UnsupportedPortfolioOperation(f"Portfolio with ID {portfolio_id} does not exist.")
            if portfolio.owner_username != logged_in_user:
                raise UnsupportedPortfolioOperation("You do not have permission to view transactions for this portfolio.")
            if security == "all":
                transactions = session.query(Transaction).filter(Transaction.portfolio_id == portfolio.id).all()
                if not transactions:
                    raise UnsupportedPortfolioOperation(f"No transactions found for Portfolio {portfolio.id}.")
            else:
                security_obj = session.query(Security).filter(Security.ticker == security).first()
                if not security_obj:
                    raise UnsupportedPortfolioOperation(f"Security with ticker {security} does not exist.")
                if security:
                    transactions = session.query(Transaction).filter(Transaction.portfolio_id == portfolio.id, Transaction.security == security).all()
                    if not transactions:
                        raise UnsupportedPortfolioOperation(f"No transactions found for security {security} in Portfolio {portfolio.id}.")
        return transactions
    finally:
        session.close() if session else None

def print_all_transactions(transactions: List[Transaction]):
    table = Table(title = "Transactions")
    table.add_column("ID", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("Portfolio ID", justify = "right", style = "magenta")
    table.add_column("Security", style = "magenta")
    table.add_column("Type", style = "magenta")
    table.add_column("Quantity", justify = "right", style = "magenta")
    table.add_column("Price", justify = "right", style = "magenta")
    table.add_column("Timestamp", style = "magenta")
    for transaction in transactions:
        table.add_row(str(transaction.id), str(transaction.portfolio_id), transaction.security, transaction.type, str(transaction.quantity), f"{transaction.price:.2f}", transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    _console.print(table)

def create_portfolio(user: User, name: str, description: str, investment_strategy: str) -> str:
    session = None
    try:
        session = db.session
        session.add(Portfolio(owner_username = user.username, name = name, description = description, investment_strategy = investment_strategy))
        session.commit()
    finally:
        session.close() if session else None

def delete_portfolio(logged_in_user: str, portfolio_id: int) -> str:
    session = None
    try:
        session = db.session
        portfolio = session.query(Portfolio).filter_by(id = portfolio_id).first()
        if portfolio is None:
            raise UnsupportedPortfolioOperation(f"Portfolio with ID {portfolio_id} does not exist.")
        if not isinstance(portfolio_id, int):
            raise UnsupportedPortfolioOperation("Portfolio ID must be an integer.")
        if portfolio.owner_username != logged_in_user:
            raise UnsupportedPortfolioOperation("You do not have permission to delete this portfolio.")
        if portfolio.investment:
            raise UnsupportedPortfolioOperation("Cannot delete a portfolio that has investments. Please harvest all investments first.")
        session.delete(portfolio)
        session.commit()
    finally:
        session.close() if session else None

def harvest_investment(logged_in_user: str, portfolio_id: int, ticker: str, quantity_input: int, sale_price: float) -> str:
    session = None
    try:
        session = db.session
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise UnsupportedPortfolioOperation(f"Portfolio with ID {portfolio_id} does not exist.")
        if portfolio.owner_username != logged_in_user:
            raise UnsupportedPortfolioOperation("You do not have permission to harvest from this portfolio.")
        portfolio_investment = session.query(Investment).filter(Investment.portfolio_id == portfolio.id, Investment.ticker == ticker).first()
        if not portfolio_investment:
            raise UnsupportedPortfolioOperation(f"No investment with ticker {ticker} found in Portfolio {portfolio.id}.")
        if quantity_input > portfolio_investment.quantity:
            raise UnsupportedPortfolioOperation("Cannot harvest more than the quantity held in the portfolio.")
        user = session.query(User).filter_by(username = logged_in_user).first()
        user.balance += quantity_input * sale_price
        portfolio_investment.quantity -= quantity_input
        if portfolio_investment.quantity == 0:
            session.delete(portfolio_investment)
        session.add(Transaction(user = user.username, portfolio_id = portfolio.id, security = ticker, type = 'SELL', quantity = quantity_input, price = sale_price, timestamp = datetime.now(timezone.utc)))
        session.commit()
    finally:
        session.close() if session else None