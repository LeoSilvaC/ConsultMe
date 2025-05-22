from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.secret_key = 'consultme-projeto'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///consultas.db'
    
    db.init_app(app)

    from .auth import auth_bp
    from .consultas import consultas_bp
    from .usuarios import usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(consultas_bp)
    app.register_blueprint(usuarios_bp)

    login_manager.init_app(app)
    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import Usuario
    return Usuario.query.get(int(user_id))