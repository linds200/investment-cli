from app.domain import User
from app.services.login_service import get_login_inputs, set_logged_in_user, reset_logged_in_user, get_logged_in_user, login

def test_get_login_inputs(monkeypatch):
    inputs = iter(['testuser', 'testpass'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    username, password = get_login_inputs()
    assert username == 'testuser'
    assert password == 'testpass'

def test_get_login_inputs_empty(monkeypatch):
    inputs = iter(['', ''])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    username, password = get_login_inputs()
    assert username == ''
    assert password == ''

def test_set_logged_in_user(db_session):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    logged_in = get_logged_in_user()
    assert logged_in is not None
    assert logged_in.username == 'testuser'

def test_set_logged_in_user_empty(db_session):
    set_logged_in_user('nonexistent')
    logged_in = get_logged_in_user()
    assert logged_in is None

def test_reset_logged_in_user(db_session):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    reset_logged_in_user()
    logged_in = get_logged_in_user()
    assert logged_in is None

def test_reset_logged_in_user_without_login():
    reset_logged_in_user()
    logged_in = get_logged_in_user()
    assert logged_in is None

def test_get_logged_in_user(db_session):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    logged_in = get_logged_in_user()
    assert logged_in is not None
    assert logged_in.username == 'testuser'

def test_get_logged_in_user_none():
    reset_logged_in_user()
    logged_in = get_logged_in_user()
    assert logged_in is None

def test_login_success(db_session, monkeypatch):
    db_session.add(User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0))
    db_session.commit()
    inputs = iter(['testuser', 'testpass'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    assert login() is True

def test_login_failure(db_session, monkeypatch, capsys):
    db_session.add(User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0))
    db_session.commit()
    inputs = iter(['testuser', 'wrongpass'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    assert login() is False
    captured = capsys.readouterr()
    assert "Invalid username or password." in captured.out