from app.domain import Security, User, Portfolio
from app.services.security_service import get_all_securities, print_all_securities, place_buy_order
from app.services.login_service import set_logged_in_user

def test_get_all_securities(db_session):
    db_session.add_all([
        Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0),
        Security(ticker = 'GOOGL', issuer = 'Alphabet Inc.', price = 2800.0),
        Security(ticker = 'MSFT', issuer = 'Microsoft Corporation', price = 300.0)
    ])
    db_session.commit()
    securities = get_all_securities()
    assert len(securities) == 3
    assert securities[0].ticker == 'AAPL'
    assert securities[1].ticker == 'GOOGL'
    assert securities[2].ticker == 'MSFT'
    
def test_get_all_securities_empty(db_session):
    securities = get_all_securities()
    assert len(securities) == 0

def test_print_all_securities(capsys, db_session):
    db_session.add_all([
        Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0),
        Security(ticker = 'GOOGL', issuer = 'Alphabet Inc.', price = 2800.0)
    ])
    db_session.commit()
    securities = get_all_securities()
    print_all_securities(securities)
    captured = capsys.readouterr()
    assert "AAPL" in captured.out
    assert "GOOGL" in captured.out

def test_print_all_securities_empty(capsys):
    securities = []
    print_all_securities(securities)
    captured = capsys.readouterr()
    assert "Available Securities" in captured.out  # Table title should still be printed

def test_place_buy_order(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 5000.0)
    portfolio = Portfolio(owner_username = 'testuser', name = 'Test Portfolio')
    security = Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0)
    db_session.add_all([user, portfolio, security])
    db_session.flush()
    portfolio_id = portfolio.id
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter([str(portfolio_id), 'AAPL', '10'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    place_buy_order()
    captured = capsys.readouterr()
    assert "Placed buy order for 10 shares of AAPL." in captured.out
    assert user.balance == 5000.0 - (150.0 * 10)

def test_place_buy_order_insufficient_balance(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 100.0)
    portfolio = Portfolio(owner_username = 'testuser', name = 'Test Portfolio')
    security = Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0)
    db_session.add_all([user, portfolio, security])
    db_session.flush()
    portfolio_id = portfolio.id
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter([str(portfolio_id), 'AAPL', '1'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    place_buy_order()
    captured = capsys.readouterr()
    assert "Insufficient balance to place buy order." in captured.out
    assert user.balance == 100.0

def test_place_buy_order_invalid_security(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 5000.0)
    portfolio = Portfolio(owner_username = 'testuser', name = 'Test Portfolio')
    db_session.add_all([user, portfolio])
    db_session.flush()
    portfolio_id = portfolio.id
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter([str(portfolio_id), 'INVALID', '10'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    place_buy_order()
    captured = capsys.readouterr()
    assert "Security with ticker 'INVALID' does not exist." in captured.out
    assert user.balance == 5000.0

def test_place_buy_order_invalid_portfolio(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 5000.0)
    security = Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0)
    db_session.add_all([user, security])
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter(['999', 'AAPL', '10'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    place_buy_order()
    captured = capsys.readouterr()
    assert "Portfolio with ID 999 does not exist." in captured.out
    assert user.balance == 5000.0

def test_place_buy_order_unauthorized_portfolio(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 5000.0)
    other_user = User(username = 'otheruser', password = 'otherpass', firstname = 'Other', lastname = 'User', balance = 3000.0)
    portfolio = Portfolio(owner_username = 'otheruser', name = 'Other Portfolio')
    security = Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0)
    db_session.add_all([user, other_user, portfolio, security])
    db_session.flush()
    portfolio_id = portfolio.id
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter([str(portfolio_id), 'AAPL', '10'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    place_buy_order()
    captured = capsys.readouterr()
    assert "You do not have permission to place a buy order for this portfolio." in captured.out
    assert user.balance == 5000.0