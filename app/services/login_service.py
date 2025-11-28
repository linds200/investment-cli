from typing import Tuple
from rich.console import Console
from app import database
from app.domain.User import User

_console = Console()

logged_in_user: User|None = None

def get_login_inputs() -> Tuple[str, str]:
    username = _console.input("Username: ")
    password = _console.input("Password: ")
    return username, password

def set_logged_in_user(username: str):
    global logged_in_user
    session = database.get_session()
    try:
        logged_in_user = session.query(User).filter_by(username = username).first()
    finally:
        session.close()

def reset_logged_in_user():
    global logged_in_user
    logged_in_user = None

def get_logged_in_user() -> User | None:
    return logged_in_user

def login() -> bool:
    session = None
    try:
        username, password = get_login_inputs()
        session = database.get_session()
        user = session.query(User).filter_by(username=username).first()
        # Invalid credentials
        if not user or user.password != password:
            _console.print("\nInvalid username or password.\n", style="bold red")
            return False
        # Valid login
        set_logged_in_user(username)
        _console.print("\nLogin Successful!\n", style="bold green")
        return True
    finally:
        if session:
            session.close()
