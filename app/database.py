from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import database_config

class Base(DeclarativeBase): pass

def create_connection_string() -> str:
    return f"mysql+pymysql://{database_config['user']}:{database_config['password']}@{database_config['host']}:{database_config['port']}/{database_config['database']}"

engine = create_engine(url = create_connection_string())
LocalSession = sessionmaker(bind = engine)

def get_session():
    return LocalSession()

def init_db(seed_securities: bool = True, seed_admin: bool = True) -> None:
    # create tables so that admin and securities can be seeded
    Base.metadata.create_all(bind = engine)

    session = LocalSession()
    try:
        added = False
        if seed_securities:
            from app.domain.Security import Security
            seeds = [
                {'ticker': 'AAPL', 'issuer': 'Apple Inc.', 'price': 175.00},
                {'ticker': 'MSFT', 'issuer': 'Microsoft Corp.', 'price': 340.00},
                {'ticker': 'GOOG', 'issuer': 'Alphabet Inc.', 'price': 130.00},
            ]
            for s in seeds:
                exists = session.query(Security).filter_by(ticker = s['ticker']).first()
                if not exists:
                    session.add(Security(ticker = s['ticker'], issuer = s['issuer'], price = s['price']))
                    added = True

        if seed_admin:
            from app.domain.User import User
            admin = session.query(User).filter_by(username = 'admin').first()
            if not admin:
                session.add(User(username = 'admin', password = 'adminpass', firstname = 'Admin', lastname = 'User', balance = 10000.0))
                added = True

        if added:
            session.commit()
    finally:
        session.close()