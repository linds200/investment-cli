from flask import Blueprint, request
from app.services.portfolio_service import get_all_portfolios, get_all_portfolios_by_user, get_portfolio_by_id, get_all_transactions, create_portfolio, delete_portfolio, harvest_investment

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/all', methods = ['GET'])
def get_all_portfolios_route():
    try:
        portfolios = get_all_portfolios()
        portfolios_data = [{
            "id": portfolio.id,
            "owner_username": portfolio.owner_username,
            "name": portfolio.name,
            "description": portfolio.description,
            "investment_strategy": portfolio.investment_strategy
        } for portfolio in portfolios]
        return {"portfolios": portfolios_data}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@portfolio_bp.route('/all/<string:username>', methods = ['GET'])
def get_all_portfolios_by_user_route(username):
    try:
        portfolios = get_all_portfolios_by_user(username)
        portfolios_data = [{
            "id": portfolio.id,
            "owner_username": portfolio.owner_username,
            "name": portfolio.name,
            "description": portfolio.description,
            "investment_strategy": portfolio.investment_strategy
        } for portfolio in portfolios]
        return {"portfolios": portfolios_data}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@portfolio_bp.route('/<int:portfolio_id>', methods = ['GET'])
def get_portfolio_by_id_route(portfolio_id):
    try:
        portfolio = get_portfolio_by_id(portfolio_id)
        portfolio_data = {
            "id": portfolio.id,
            "owner_username": portfolio.owner_username,
            "name": portfolio.name,
            "description": portfolio.description,
            "investment_strategy": portfolio.investment_strategy
        }
        return {"portfolio": portfolio_data}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@portfolio_bp.route('/transactions', methods = ['GET'])
def get_all_transactions_route():
    try:
        logged_in_user = request.args.get('logged_in_user')
        portfolio_id = request.args.get('portfolio_id')
        security = request.args.get('security')
        transactions = get_all_transactions(logged_in_user, portfolio_id, security)
        transactions_data = [{
            "id": transaction.id,
            "portfolio_id": transaction.portfolio_id,
            "security": transaction.security,
            "type": transaction.type,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "timestamp": transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for transaction in transactions]
        return {"transactions": transactions_data}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@portfolio_bp.route('/create', methods = ['POST'])
def create_portfolio_route():
    data = request.get_json()
    try:
        user = data.get('user')
        name = data.get('name')
        description = data.get('description')
        investment_strategy = data.get('investment_strategy')
        create_portfolio(user, name, description, investment_strategy)
        return {"message": f"Portfolio {name} created for user {user}."}, 201
    except Exception as e:
        return {"error": str(e)}, 400

@portfolio_bp.route('/delete/<int:portfolio_id>', methods = ['DELETE'])
def delete_portfolio_route(portfolio_id):
    data = request.get_json()
    try:
        logged_in_user = data.get('logged_in_user')
        delete_portfolio(logged_in_user, portfolio_id)
        return {"message": f"Portfolio with ID {portfolio_id} deleted successfully."}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@portfolio_bp.route('/harvest', methods = ['POST'])
def harvest_investment_route():
    data = request.get_json()
    try:
        logged_in_user = data.get('logged_in_user')
        portfolio_id = int(data.get('portfolio_id'))
        ticker = data.get('ticker')
        quantity_input = int(data.get('quantity_input'))
        sale_price = float(data.get('sale_price'))
        harvest_investment(logged_in_user, portfolio_id, ticker, quantity_input, sale_price)
        return {"message": f"Harvested investment in {ticker} from Portfolio {portfolio_id}."}, 200
    except Exception as e:
        return {"error": str(e)}, 400