from datetime import datetime
from flask import Flask,request,render_template,url_for,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from sqlalchemy import  and_, func

app = Flask(__name__)
app.secret_key = 'consultme-projeto'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///consultas.db'
db = SQLAlchemy(app)



#Iniciar a Aplicação
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
