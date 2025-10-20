from typing import Dict, List
from domain.User import User
from domain.Security import Security
from domain.Portfolio import Portfolio
from domain.Investment import Investment

class UniqueConstraintError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

next_portfolio_id = 1

_users: Dict[str, User] = {
    'admin': User("admin", "adminpass", "Admin Firstname", "Admin Lastname", 0)
    }

_securities: Dict[str, Security] = {
    "AAPL": Security("AAPL", "Apple Inc.", 150.00),
    "GOOGL": Security("GOOGL", "Alphabet Inc.", 2800.00),
    "AMZN": Security("AMZN", "Amazon.com Inc.", 3400.00)
}

_portfolios: Dict[str, Portfolio] = {}

logged_in_user: User|None = None

def get_logged_in_user() -> User|None:
    return logged_in_user

def set_logged_in_user(user: User):
    global logged_in_user
    logged_in_user = user

def reset_logged_in_user():
    global logged_in_user
    logged_in_user = None

def query_user(username: str) -> User | None:
    try:
        return _users.get(username)
    except KeyError:
        return None

def query_all_users() -> List[User]:
    return list(_users.values())

def create_new_user(user: User):
    if user.username in _users:
        raise UniqueConstraintError(f"User with username {user.username} already exists")
    _users[user.username] = user

def delete_user(username: str):
    if username not in _users:
        raise UniqueConstraintError(f"User with username {username} does not exist")
    if username == "admin":
        raise UniqueConstraintError("Cannot delete admin user")
    else:
        del _users[username]

def get_all_portfolios_logged_in_user() -> List[Portfolio]:
    user = get_logged_in_user()
    if not user:
        return []
    return [p for p in _portfolios.values() if p.owner_username == user.username]

def create_new_portfolio(portfolio: Portfolio):
    global next_portfolio_id
    if portfolio.id in _portfolios:
        raise UniqueConstraintError(f"Portfolio with id {portfolio.id} already exists")
    _portfolios[portfolio.id] = portfolio
    next_portfolio_id += 1

def delete_portfolio(portfolio_id: str):
    if portfolio_id not in _portfolios:
        raise UniqueConstraintError(f"Portfolio with id {portfolio_id} does not exist")
    user = get_logged_in_user()
    if not user or _portfolios[portfolio_id].owner_username != user.username:
        raise UniqueConstraintError("Cannot delete portfolio not owned by the logged-in user")
    if len(_portfolios[portfolio_id].holdings) > 0:
        raise UniqueConstraintError("Cannot delete portfolio with holdings")
    else:
        del _portfolios[portfolio_id]

def harvest_investment(portfolio_id: str, ticker: str, quantity: int, sale_price: float):
    if portfolio_id not in _portfolios:
        raise UniqueConstraintError(f"Portfolio with id {portfolio_id} does not exist")
    user = get_logged_in_user()
    if not user or _portfolios[portfolio_id].owner_username != user.username:
        raise UniqueConstraintError("Cannot harvest investment from portfolio not owned by the logged-in user")
    portfolio = _portfolios[portfolio_id]
    for holding in portfolio.holdings:
        if holding[0].ticker == ticker:
            if quantity > holding[1]:
                raise UniqueConstraintError("Cannot harvest more than owned quantity")
            holding[1] -= quantity
            if holding[1] == 0:
                Portfolio.remove_holding(portfolio, ticker, 0)
            get_logged_in_user().balance += sale_price * quantity
            return
    raise UniqueConstraintError(f"No investments found for ticker {ticker} in portfolio {portfolio_id}")

def get_all_securities() -> List[Security]:
    return list(_securities.values())

def place_buy_order(portfolio_id: str, ticker: str, quantity: int):
    if portfolio_id not in _portfolios:
        raise UniqueConstraintError(f"Portfolio with id {portfolio_id} does not exist")
    user = get_logged_in_user()
    if not user or _portfolios[portfolio_id].owner_username != user.username:
        raise UniqueConstraintError("Cannot place buy order for portfolio not owned by the logged-in user")
    if ticker not in _securities:
        raise UniqueConstraintError(f"Security with ticker {ticker} does not exist")
    price = _securities[ticker].reference_price * quantity
    if price > get_logged_in_user().balance:
        raise UniqueConstraintError("Insufficient balance to place buy order")
    else:
        get_logged_in_user().balance -= price
        portfolio = _portfolios[portfolio_id]
        for holding in portfolio.holdings:
            if holding[0].ticker == ticker:
                holding[1] += quantity
                return
        Portfolio.add_holding(portfolio, _securities[ticker], quantity)