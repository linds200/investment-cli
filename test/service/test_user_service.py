from app.domain import User, Portfolio
from app.services.user_service import get_all_users, get_user_by_username, print_all_users, create_user, delete_user

def test_get_all_users(db_session):
    db_session.add_all([
        User(username = 'test1', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0),
        User(username = 'test2', password = 'testpass', firstname = 'Test', lastname = 'User2', balance = 1500.0)
    ])
    db_session.commit()
    users = get_all_users()
    assert len(users) == 2
    assert users[0].username == 'test1'
    assert users[1].username == 'test2'

def test_get_all_users_empty(db_session):
    users = get_all_users()
    assert len(users) == 0

def test_get_user_by_username(db_session):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 500.0)
    db_session.add(user)
    db_session.commit()
    fetched_user = get_user_by_username('testuser')
    assert fetched_user is not None
    assert fetched_user.username == 'testuser'

def test_get_user_by_username_not_found(db_session):
    fetched_user = get_user_by_username('nonexistent')
    assert fetched_user is None

def test_print_all_users(capsys, db_session):
    db_session.add_all([
        User(username = 'test1', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0),
        User(username = 'test2', password = 'testpass', firstname = 'Test', lastname = 'User2', balance = 1500.0)
    ])
    db_session.commit()
    users = get_all_users()
    print_all_users(users)
    captured = capsys.readouterr()
    assert "test1" in captured.out
    assert "test2" in captured.out

def test_print_all_users_empty(capsys):
    users = []
    print_all_users(users)
    captured = capsys.readouterr()
    assert "Registered Users" in captured.out  # Table title should still be printed

def test_create_user(db_session, monkeypatch, capsys):
    inputs = iter(['newuser', 'newpass', 'New', 'User', '2000'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    create_user()
    user = db_session.query(User).filter_by(username='newuser').first()
    assert user is not None
    assert user.firstname == 'New'
    captured = capsys.readouterr()
    assert "User newuser created successfully." in captured.out

def test_create_user_invalid_balance(monkeypatch, capsys):
    inputs = iter(['newuser', 'newpass', 'New', 'User', 'invalid'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    create_user()
    captured = capsys.readouterr()
    assert "Invalid input. Please try again." in captured.out

def test_delete_user(db_session, monkeypatch, capsys):
    user = User(username = 'tobedeleted', password = 'pass', firstname = 'To', lastname = 'Delete', balance = 300.0)
    db_session.add(user)
    db_session.commit()
    inputs = iter(['tobedeleted'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    delete_user()
    captured = capsys.readouterr()
    assert "User tobedeleted deleted successfully." in captured.out

def test_delete_user_not_found(monkeypatch, capsys):
    inputs = iter(['nonexistent'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    delete_user()
    captured = capsys.readouterr()
    assert "User with username nonexistent does not exist" in captured.out

def test_delete_user_admin_protected(db_session, monkeypatch, capsys):
    user = User(username = 'admin', password = 'pass', firstname = 'Admin', lastname = 'User', balance = 5000.0)
    db_session.add(user)
    db_session.commit()
    inputs = iter(['admin'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    delete_user()
    captured = capsys.readouterr()
    assert "Cannot delete admin user" in captured.out

def test_delete_user_with_portfolios(db_session, monkeypatch, capsys):
    user = User(username = 'owner', password = 'pass', firstname = 'Owner', lastname = 'User', balance = 1000.0)
    portfolio = Portfolio(owner_username = 'owner', name = 'Owner Portfolio', description = 'Desc', investment_strategy = 'Strategy')
    db_session.add_all([user, portfolio])
    db_session.commit()
    inputs = iter(['owner'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    delete_user()
    captured = capsys.readouterr()
    assert "Cannot delete user owner who owns portfolios." in captured.out