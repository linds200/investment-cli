from typing import List
from rich.console import Console
from rich.table import Table
import db
from domain.Security import Security

_console = Console()

def get_all_securities() -> List[Security]:
    return db.get_all_securities()

def print_all_securities(securities: List[Security]):
    table = Table(title = "Available Securities")
    table.add_column("Ticker", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("Issuer", style = "magenta")
    table.add_column("Reference Price", justify = "right", style = "green")
    for security in securities:
        table.add_row(security.ticker, security.issuer, f"${security.reference_price:.2f}")
    _console.print(table)

def place_buy_order() -> str:
    portfolio = _console.input("Enter Portfolio ID to use for Purchase: ")
    ticker = _console.input("Enter Ticker of Security to Buy: ")
    quantity_input = int(_console.input("Enter Quantity to Buy: "))
    db.place_buy_order(portfolio, ticker, quantity_input)
    _console.print(f"\nPlaced buy order for {quantity_input} shares of {ticker}.\n", style = "bold green")