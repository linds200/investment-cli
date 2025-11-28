from app.domain import Portfolio, User, Security, Investment
from app.services.login_service import set_logged_in_user, get_logged_in_user
from app.services.security_service import place_buy_order
from app.services.portfolio_service import create_portfolio, delete_portfolio, get_all_portfolios, print_all_portfolios, harvest_investment

def test_create_portfolio(db_session, monkeypatch):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter(['My Portfolio', 'A test portfolio', 'Aggressive'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    create_portfolio()
    portfolio = db_session.query(Portfolio).filter_by(name='My Portfolio', owner_username='testuser').first()
    assert portfolio is not None
    assert portfolio.description == 'A test portfolio'
    assert portfolio.investment_strategy == 'Aggressive'

def test_delete_portfolio(db_session, monkeypatch):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    set_logged_in_user('testuser')
    inputs = iter(['My Portfolio', 'A test portfolio', 'Aggressive'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    create_portfolio()
    portfolio = db_session.query(Portfolio).filter_by(name='My Portfolio', owner_username='testuser').first()
    inputs = iter([str(portfolio.id)])
    delete_portfolio()
    deleted_portfolio = db_session.query(Portfolio).filter_by(id=portfolio.id).first()
    assert deleted_portfolio is None

def test_delete_portfolio_not_found(db_session, monkeypatch, capsys):
    inputs = iter(['9999'])  # Non-existent portfolio ID
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    delete_portfolio()
    captured = capsys.readouterr()
    assert "does not exist" in captured.out

def test_delete_portfolio_no_permission(db_session, monkeypatch, capsys):
    user1 = User(username = 'user1', password = 'pass1', firstname = 'User', lastname = 'One', balance = 1000.0)
    user2 = User(username = 'user2', password = 'pass2', firstname = 'User', lastname = 'Two', balance = 1000.0)
    db_session.add_all([user1, user2])
    db_session.commit()
    set_logged_in_user('user1')
    inputs = iter(['User1 Portfolio', 'Portfolio of user1', 'Conservative'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    create_portfolio()
    portfolio = db_session.query(Portfolio).filter_by(name='User1 Portfolio', owner_username='user1').first()
    set_logged_in_user('user2')
    inputs = iter([str(portfolio.id)])
    delete_portfolio()
    captured = capsys.readouterr()
    assert "do not have permission" in captured.out

def test_delete_portfolio_invalid_input(monkeypatch, capsys):
    inputs = iter(['invalid'])  # Non-integer input
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    delete_portfolio()
    captured = capsys.readouterr()
    assert "Invalid input" in captured.out

def test_delete_portfolio_with_investments(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    security = Security(ticker='AAPL', issuer='Apple Inc.', price=150.0)
    db_session.add_all([user, security])
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter(['Test Portfolio', 'A test portfolio', 'Balanced'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    create_portfolio()
    portfolio = db_session.query(Portfolio).filter_by(name='Test Portfolio', owner_username='testuser').first()
    investment = Investment(portfolio_id=portfolio.id, ticker='AAPL', quantity=10)
    db_session.add(investment)
    db_session.commit()
    inputs = iter([str(portfolio.id)])
    delete_portfolio()
    captured = capsys.readouterr()
    assert "Cannot delete a portfolio that has investments" in captured.out

def test_get_all_portfolios(db_session):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    portfolio1 = Portfolio(owner_username='testuser', name='Portfolio1', description='Desc1', investment_strategy='Strategy1')
    portfolio2 = Portfolio(owner_username='testuser', name='Portfolio2', description='Desc2', investment_strategy='Strategy2')
    db_session.add_all([portfolio1, portfolio2])
    db_session.commit()
    portfolios = get_all_portfolios()
    assert len(portfolios) == 2
    assert portfolios[0].name == 'Portfolio1'
    assert portfolios[1].name == 'Portfolio2'

def test_get_all_portfolios_empty(db_session, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    portfolios = get_all_portfolios()
    captured = capsys.readouterr()
    assert len(portfolios) == 0
    assert "No portfolios found" in captured.out

def test_print_all_portfolios(capsys, db_session):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    portfolio1 = Portfolio(owner_username='testuser', name='Portfolio1', description='Desc1', investment_strategy='Strategy1')
    portfolio2 = Portfolio(owner_username='testuser', name='Portfolio2', description='Desc2', investment_strategy='Strategy2')
    db_session.add_all([portfolio1, portfolio2])
    db_session.commit()
    portfolios = get_all_portfolios()
    print_all_portfolios(portfolios)
    captured = capsys.readouterr()
    assert "Portfolio1" in captured.out
    assert "Portfolio2" in captured.out

def test_print_all_portfolios_empty(capsys):
    portfolios = []
    print_all_portfolios(portfolios)
    captured = capsys.readouterr()
    assert "Portfolios" in captured.out  # Table title should still be printed  

def test_harvest_investment(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    security = Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0)
    portfolio = Portfolio(owner_username = 'testuser', name = 'Test Portfolio', description = 'Desc', investment_strategy = 'Strategy')
    db_session.add_all([user, security, portfolio])
    db_session.flush()
    portfolio_id = portfolio.id
    investment = Investment(portfolio_id = portfolio.id, ticker = 'AAPL', quantity = 20)
    db_session.add(investment)
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter([str(portfolio_id), 'AAPL', '10', '150.0'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    harvest_investment()
    updated_investment = db_session.query(Investment).filter_by(portfolio_id=portfolio_id, ticker='AAPL').first()
    assert updated_investment.quantity == 10
    updated_user = db_session.query(User).filter_by(username='testuser').first()
    assert updated_user.balance == 1000.0 + (150.0 * 10)
    captured = capsys.readouterr()
    assert "Harvested 10 shares of AAPL" in captured.out

def test_harvest_investment_insufficient_quantity(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    security = Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0)
    portfolio = Portfolio(owner_username = 'testuser', name = 'Test Portfolio', description = 'Desc', investment_strategy = 'Strategy')
    db_session.add_all([user, security, portfolio])
    db_session.flush()
    portfolio_id = portfolio.id
    investment = Investment(portfolio_id = portfolio.id, ticker = 'AAPL', quantity = 5)
    db_session.add(investment)
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter([str(portfolio_id), 'AAPL', '10', '150.0'])  # Trying to harvest more than owned
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    harvest_investment()
    captured = capsys.readouterr()
    assert "Insufficient quantity" in captured.out

def test_harvest_investment_invalid_portfolio(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    db_session.add(user)
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter(['9999', 'AAPL', '10', '150.0'])  # Non-existent portfolio ID
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    harvest_investment()
    captured = capsys.readouterr()
    assert "Portfolio with ID 9999 does not exist." in captured.out

def test_harvest_investment_no_permission(db_session, monkeypatch, capsys):
    user1 = User(username = 'user1', password = 'pass1', firstname = 'User', lastname = 'One', balance = 1000.0)
    user2 = User(username = 'user2', password = 'pass2', firstname = 'User', lastname = 'Two', balance = 1000.0)
    security = Security(ticker = 'AAPL', issuer = 'Apple Inc.', price = 150.0)
    portfolio = Portfolio(owner_username = 'user1', name = 'User1 Portfolio', description = 'Desc', investment_strategy = 'Strategy')
    db_session.add_all([user1, user2, security, portfolio])
    db_session.flush()
    portfolio_id = portfolio.id
    investment = Investment(portfolio_id = portfolio.id, ticker = 'AAPL', quantity = 20)
    db_session.add(investment)
    db_session.commit()
    set_logged_in_user('user2')  # Different user
    inputs = iter([str(portfolio_id), 'AAPL', '10', '150.0'])
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    harvest_investment()
    captured = capsys.readouterr()
    assert "do not have permission" in captured.out

def test_harvest_investment_investment_not_found(db_session, monkeypatch, capsys):
    user = User(username = 'testuser', password = 'testpass', firstname = 'Test', lastname = 'User', balance = 1000.0)
    portfolio = Portfolio(owner_username = 'testuser', name = 'Test Portfolio', description = 'Desc', investment_strategy = 'Strategy')
    db_session.add_all([user, portfolio])
    db_session.flush()
    portfolio_id = portfolio.id
    db_session.commit()
    set_logged_in_user('testuser')
    inputs = iter([str(portfolio_id), 'AAPL', '10', '150.0'])  # No investment in AAPL
    monkeypatch.setattr('rich.console.Console.input', lambda self, prompt: next(inputs))
    harvest_investment()
    captured = capsys.readouterr()
    assert "No investment with ticker AAPL found" in captured.out