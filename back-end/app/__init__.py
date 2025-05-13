from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    return app
