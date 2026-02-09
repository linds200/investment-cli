from flask import Flask
from app.db import db
from app.routes.portfolio_bp import portfolio_bp
from app.routes.user_bp import user_bp
from app.routes.security_bp import security_bp

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(security_bp, url_prefix='/security')

    return app