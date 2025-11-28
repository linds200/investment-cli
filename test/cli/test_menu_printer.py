import pytest
from app.cli.menu_printer import print_menu, handle_user_selection, print_error, navigate_to_manage_users_menu
from app.cli import constants
from app.services.login_service import set_logged_in_user
from app.domain import User

def test_handle_user_selection_logout(monkeypatch, capsys):
    inputs = iter(["0", "0"])   # Simulate user input '0' to logout
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    user = User(username="admin", password="testpass", firstname="Test", lastname="User", balance=1000.0)
    set_logged_in_user("admin")  # Mock a logged-in user
    with pytest.raises(SystemExit):
        print_menu(constants.main_menu)
    captured = capsys.readouterr()
    assert "Login" in captured.out  # Check that we returned to login menu

def test_handle_user_selection_invalid_input(monkeypatch):
    inputs = iter(["invalid", "0"])  # First invalid input, then exit
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    with pytest.raises(SystemExit):
        print_menu(constants.login_menu)

def test_print_error(capsys):
    test_message = "This is a test error."
    print_error(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.out

def test_print_menu_invalid_input(monkeypatch, capsys):
    inputs = iter(["invalid", "0"])  # First invalid input, then exit
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    with pytest.raises(SystemExit):
        print_menu(constants.login_menu)
    captured = capsys.readouterr()
    assert "Invalid input. Please enter a number." in captured.out

def test_print_menu_invalid_option(monkeypatch, capsys):
    inputs = iter(["99", "0"])  # First invalid option, then exit
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    with pytest.raises(SystemExit):
        print_menu(constants.login_menu)
    captured = capsys.readouterr()
    assert "Error" in captured.out  # Check that an error message was printed

def test_print_menu_login(monkeypatch, capsys):
    input = iter(['0'])  # Simulate user input '0' to exit
    monkeypatch.setattr('builtins.input', lambda prompt='': next(input))
    with pytest.raises(SystemExit):
        print_menu(constants.login_menu)
    captured = capsys.readouterr()
    assert "Login" in captured.out  # Check that the prompt was printed

def test_print_menu_main(monkeypatch, capsys):
    inputs = iter(["1", "0", "0", "0", "0"]) # Simulate user input '0' to logout
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    user = User(username="admin", password="testpass", firstname="Test", lastname="User", balance=1000.0)
    set_logged_in_user("admin")  # Mock a logged-in user
    with pytest.raises(SystemExit):
        print_menu(constants.main_menu)
    captured = capsys.readouterr()
    assert "Main Menu" in captured.out  # Check that the prompt was printed

def test_navigate_to_manage_users_menu(monkeypatch):
    user = User(username="admin", password="testpass", firstname="Test", lastname="User", balance=1000.0)
    set_logged_in_user("admin")  # Mock admin user
    menu_id = navigate_to_manage_users_menu()
    assert menu_id == constants.manager_users_menu