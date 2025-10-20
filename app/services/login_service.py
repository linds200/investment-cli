from typing import Tuple
from rich.console import Console
import db

_console = Console()

class UnsupportedMenuError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

def get_login_inputs() -> Tuple[str, str]:
    username = _console.input("Username: ")
    password = _console.input("Password: ")
    return username, password

def login():
    username, password = get_login_inputs()
    user = db.query_user(username)
    if not user or user.password != password:
        raise UnsupportedMenuError("Invalid username or password.")
    else:
        _console.print("\nLogin Successful!\n", style = "bold green")
    db.set_logged_in_user(user)     