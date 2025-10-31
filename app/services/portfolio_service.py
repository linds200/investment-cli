from typing import List
from rich.console import Console
from rich.table import Table
import db
from domain.Portfolio import Portfolio

_console = Console()

class UnsupportedMenuError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

def get_all_portfolios() -> List[Portfolio]:
    portfolios =  db.get_all_portfolios_logged_in_user()
    if not portfolios:
        raise UnsupportedMenuError("No portfolios found for the logged-in user.")
    return portfolios

def print_all_portfolios(portfolios: List[Portfolio]):
    table = Table(title = "Portfolios")
    table.add_column("ID", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("Owner", style = "magenta")
    table.add_column("Name", style = "magenta")
    table.add_column("Description", style = "magenta")
    table.add_column("Investment Strategy", style = "magenta")
    for portfolio in portfolios:
        table.add_row(portfolio.id, portfolio.owner_username, portfolio.name, portfolio.description, portfolio.investment_strategy)
    _console.print(table)

def create_portfolio() -> str:
    name = _console.input("Enter Portfolio Name: ")
    description = _console.input("Enter Portfolio Description: ")
    investment_strategy = _console.input("Enter Investment Strategy: ")
    portfolio_id = str(db.next_portfolio_id)
    owner_username = db.get_logged_in_user().username
    portfolio = Portfolio(portfolio_id, owner_username, name, description, investment_strategy, [])
    db.create_new_portfolio(portfolio)
    _console.print(f"\nPortfolio {name} created successfully with ID {portfolio_id}.\n", style = "bold green")

def delete_portfolio() -> str:
    portfolio_id = _console.input("Enter Portfolio ID to delete: ")
    db.delete_portfolio(portfolio_id)
    _console.print(f"\nPortfolio with ID {portfolio_id} deleted successfully.\n", style = "bold green")

def harvest_investment() -> str:
    portfolio_id = _console.input("Enter Portfolio ID to harvest from: ")
    ticker = _console.input("Enter Ticker of Investment to harvest: ")
    quantity_input = int(_console.input("Enter Quantity to harvest: "))
    sale_price = float(_console.input("Enter Sale Price per Unit: "))
    db.harvest_investment(portfolio_id, ticker, quantity_input, sale_price)
    _console.print(f"\nHarvested {quantity_input} shares of {ticker} from Portfolio {portfolio_id}.\n", style = "bold green")