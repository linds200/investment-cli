from domain.Security import Security

class Portfolio:
    def __init__(self, id: str, owner_username: str, name: str, description, investment_strategy: str, holdings: list = []):
        self.id = id
        self.owner_username = owner_username
        self.name = name
        self.description = description
        self.investment_strategy = investment_strategy
        self.holdings = holdings  # List of tuples (Security, quantity)
    
    def add_holding(self, security: 'Security', quantity: int):
        for holding in self.holdings:
            if holding[0].ticker == security.ticker:
                holding[1] += quantity
                return
        self.holdings.append([security, quantity])
    
    def remove_holding(self, ticker: str, quantity: int):
        for holding in self.holdings:
            if holding[0].ticker == ticker:
                if quantity > holding[1]:
                    raise ValueError("Cannot remove more than owned quantity")
                holding[1] -= quantity
                if holding[1] == 0:
                    self.holdings.remove(holding)
                return
        raise ValueError(f"No holdings found for ticker {ticker}")