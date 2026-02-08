from flask import Blueprint, request
from app.services.security_service import get_all_securities, place_buy_order

security_bp = Blueprint('security', __name__)

@security_bp.route('/all', methods = ['GET'])
def get_all_securities_route():
    try:
        securities = get_all_securities()
        securities_data = [{
            "ticker": security.ticker,
            "issuer": getattr(security, 'issuer', None),
            "price": getattr(security, 'price', None)
        } for security in securities]
        return {"securities": securities_data}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@security_bp.route('/buy', methods = ['POST'])
def place_buy_order_route():
    data = request.get_json()
    try:
        logged_in_user = data['logged_in_user']
        portfolio_id = int(data['portfolio_id'])
        ticker = data['ticker']
        quantity_input = int(data['quantity_input'])
        place_buy_order(logged_in_user, portfolio_id, ticker, quantity_input)
        return {"message": f"Buy order for {quantity_input} shares of {ticker} placed successfully in portfolio {portfolio_id}."}, 201
    except Exception as e:
        return {"error": str(e)}, 400