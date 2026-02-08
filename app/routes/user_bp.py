from flask import Blueprint, request
from app.services.user_service import get_all_users, get_user_by_username, create_user, delete_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/all', methods = ['GET'])
def get_all_users_route():
    try:
        users = get_all_users()
        users_data = [{
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "balance": user.balance
        } for user in users]
        return {"users": users_data}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@user_bp.route('/<string:username>', methods = ['GET'])
def get_user_by_username_route(username):
    try:
        user = get_user_by_username(username)
        user_data = {
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "balance": user.balance
        }
        return {"user": user_data}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@user_bp.route('/create', methods = ['POST'])
def create_user_route():
    data = request.get_json()
    try:
        logged_in_user = data['logged_in_user']
        username = data['username']
        password = data['password']
        firstname = data['firstname']
        lastname = data['lastname']
        balance_input = data['balance_input']
        create_user(logged_in_user,username, password, firstname, lastname, balance_input)
        return {"message": f"User {username} created successfully."}, 201
    except Exception as e:
        return {"error": str(e)}, 400

@user_bp.route('/delete/<string:username>', methods = ['DELETE'])
def delete_user_route(username):
    data = request.get_json()
    try:
        logged_in_user = data['logged_in_user']
        delete_user(logged_in_user, username)
        return {"message": f"User {username} deleted successfully."}, 200
    except Exception as e:
        return {"error": str(e)}, 400