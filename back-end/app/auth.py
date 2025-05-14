from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Usuario
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def efetua_login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_tipo'] = usuario.tipo
            session['usuario_nome'] = usuario.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('consultas.listar_consultas'))
        else:
            flash('E-mail ou senha inválidos', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso.")
    return redirect(url_for('auth.efetua_login'))