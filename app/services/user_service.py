from typing import List
from rich.console import Console
from rich.table import Table
from app import database
from app.domain.User import User

_console = Console()

def get_all_users() -> List[User]:
    session = None
    try:
        session = database.get_session()
        return session.query(User).all()
    except Exception as e:
        _console.print(f"\nFailed to retrieve users: {e}\n", style="bold red")
        return []
    finally:
        if session:
            session.close()


def get_user_by_username(username: str) -> User | None:
    try:
        session = database.get_session()
        user = session.query(User).filter(User.username == username).first()
    finally:
        session.close() if session else None
    return user

def print_all_users(users: List[User]):
    table = Table(title = "Registered Users")
    table.add_column("Username", justify = "right", style = "cyan", no_wrap = True)
    table.add_column("First Name", style = "magenta")
    table.add_column("Last Name", style = "magenta")
    table.add_column("Balance", justify = "right", style = "green")
    for user in users:
        table.add_row(user.username, user.firstname, user.lastname, f"${user.balance:.2f}")
    _console.print(table)

def create_user() -> str:
    session = None
    try:
        username = _console.input("Enter Username: ")
        password = _console.input("Enter Password: ")
        firstname = _console.input("Enter First Name: ")
        lastname = _console.input("Enter Last Name: ")
        balance_input = float(_console.input("Enter Initial Balance: "))
        session = database.get_session()
        session.add(User(username=username, password=password, firstname=firstname, lastname=lastname, balance=balance_input))
        session.commit()
        _console.print(f"\nUser {username} created successfully.\n", style = "bold green")
    except ValueError:
        _console.print("\nInvalid input. Please try again.\n", style = "bold red")
    finally:
        session.close() if session else None

def delete_user() -> str:
    session = None
    try:
        username = _console.input("Enter Username of user to delete: ")
        if username == "admin":
            _console.print("\nCannot delete admin user\n", style="bold red")
            return
        session = database.get_session()
        user = session.query(User).filter(User.username == username).first()
        if not user:
            _console.print(f"\nUser with username {username} does not exist\n", style="bold red")
            return
        if user.portfolio:
            _console.print(f"\nCannot delete user {username} who owns portfolios. Please delete all portfolios first.\n", style="bold red")
            return
        session.delete(user)
        session.commit()
        _console.print(f"\nUser {username} deleted successfully.\n", style = "bold green")
    except Exception as e:
        _console.print(f"\nError deleting user: {e}\n", style = "bold red")
    finally:
        session.close() if session else None