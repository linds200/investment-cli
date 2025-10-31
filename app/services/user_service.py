from typing import List
from rich.console import Console
from rich.table import Table
import db
from domain.User import User

_console = Console()

def get_all_users() -> List[User]:
    return db.query_all_users()

def print_all_users(users: List[User]):
    table = Table(title = "Registered Users")
    table.add_column("Username", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("First Name", style = "magenta")
    table.add_column("Last Name", style = "magenta")
    table.add_column("Balance", justify = "right", style = "green")
    for user in users:
        table.add_row(user.username, user.firstname, user.lastname, f"${user.balance:.2f}")
    _console.print(table)

def create_user() -> User:
    username = _console.input("Enter Username: ")
    password = _console.input("Enter Password: ")
    firstname = _console.input("Enter First Name: ")
    lastname = _console.input("Enter Last Name: ")
    balance_input = float(_console.input("Enter Initial Balance: "))
    db.create_new_user(User(username, password, firstname, lastname, balance_input))
    _console.print(f"\nUser {username} created successfully.\n", style = "bold green")

def delete_user() -> str:
    username = _console.input("Enter Username of user to delete: ")
    db.delete_user(username)
    _console.print(f"\nUser {username} deleted successfully.\n", style = "bold green")