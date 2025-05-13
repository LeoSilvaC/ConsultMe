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
            return redirect(url_for('consultas.lista_consultas'))
        else:
            flash('E-mail ou senha inválidos', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso.")
    return redirect(url_for('auth.efetua_login'))

@auth_bp.route('/cadastro')
def exibe_formulario_usuario():
    return render_template('cadastra_usuario.html')

@auth_bp.route('/cadastra_usuario', methods=["POST"])
def cadastra_usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    tipo = request.form['tipo']

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        flash('E-mail já cadastrado. Use outro.', 'warning')
        return redirect(url_for('auth.exibe_formulario_usuario'))

    novo_usuario = Usuario(nome=nome, email=email, senha=senha, tipo=tipo)
    db.session.add(novo_usuario)
    db.session.commit()
    flash('Usuário cadastrado com sucesso! Faça login.', 'success')
    return redirect(url_for('auth.efetua_login'))
