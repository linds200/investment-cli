from typing import List
from rich.console import Console
from rich.table import Table
from app.db import db
from app.domain.User import User

_console = Console()

class UnsupportedUserOperation(Exception):
    pass

def get_all_users() -> List[User]:
    session = None
    try:
        session = db.session
        users = session.query(User).all()
        if not users:
            raise UnsupportedUserOperation("No users found.")
    finally:
        session.close() if session else None
    return users

def get_user_by_username(username: str) -> User:
    session = None
    try:
        session = db.session
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise UnsupportedUserOperation(f"User {username} does not exist.")
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

def create_user(logged_in_user: str, username: str, password: str, firstname: str, lastname: str, balance_input: int) -> str:
    session = None
    try:
        if logged_in_user != "admin":
            raise UnsupportedUserOperation("Only admin can create new users.")
        if username in [user.username for user in get_all_users()]:
            raise UnsupportedUserOperation(f"User {username} already exists.")
        if not isinstance(balance_input, int):
            raise UnsupportedUserOperation("Balance must be an integer.")
        if balance_input < 0:
            raise UnsupportedUserOperation("Balance cannot be negative.")
        session = db.session
        session.add(User(username = username, password = password, firstname = firstname, lastname = lastname, balance = balance_input))
        session.commit()
    finally:
        session.close() if session else None

def delete_user(logged_in_user: str, username: str) -> str:
    session = None
    try:
        if logged_in_user != "admin":
            raise UnsupportedUserOperation("Only admin can delete users.")
        if username == "admin":
            raise UnsupportedUserOperation("Cannot delete admin user.")
        session = db.session
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise UnsupportedUserOperation(f"User {username} does not exist.")
        if user.portfolio:
            raise UnsupportedUserOperation(f"User {username} has associated portfolios and cannot be deleted.")
        session.delete(user)
        session.commit()
    finally:
        session.close() if session else None