class Security:
    def __init__(self, ticker: str, issuer: str, reference_price: float):
        self.ticker = ticker
        self.issuer = issuer
        self.reference_price = reference_price