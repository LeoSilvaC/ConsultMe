from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Usuario
from .consultas import login_required, admin_required
from sqlalchemy import  and_, func
from . import db

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/', methods=['GET', 'POST'])
def efetua_login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        
        usuario_existe = Usuario.query.filter_by(email=email, senha=senha).first()
        
        if usuario_existe:
            session['usuario_id'] = usuario_existe.email
            session['usuario_tipo'] = usuario_existe.tipo
            return redirect(url_for('consulta.listar_consultas'))
        else:
            flash('Email/Senha está incorreto')
   
    return render_template('auth/login.html')

@usuarios_bp.route('/cadastro', methods=['GET'])
@login_required
@admin_required
def exibe_formulario_usuario():
    return render_template('usuarios/cadastra_usuario.html')

#Cadastro de novo usuario
@usuarios_bp.route('/cadastra_usuario', methods=["GET", "POST"])
@login_required
@admin_required
def cadastra_usuario():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,
            tipo=tipo
        )

        email_existente = Usuario.query.filter_by(email=email).first()

        if email_existente:
            flash("Email já cadastrado!")
        else:
            db.session.add(novo_usuario)
            db.session.commit()
            return redirect(url_for('auth.efetua_login'))

    return render_template('usuarios/cadastra_usuario.html')

@usuarios_bp.route('/listar_usuarios', methods=['GET'])
@login_required
@admin_required
def listar_usuarios():
    nome = request.args.get('nome')
    usuarios = Usuario.query  
    
    if nome:
        nome.lower()
        usuarios = usuarios.filter(func.lower(Usuario.nome).like(f"%{nome.lower()}%"))

    usuarios = usuarios.all()
    return render_template('usuarios/listar_usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def excluir_usuario(id):
    usuario = Usuario.query.get(id)
    
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return {'mensagem': 'Usuario excluída com sucesso!'}
    else:
        return {'erro': 'Usuario não encontrada'}, 404

#Rota do formulário que edita um usuario
@usuarios_bp.route('/editar_usuario/<int:id>', methods=["GET"])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template('usuarios/editar_usuario.html', usuario=usuario)

@usuarios_bp.route('/atualizar_usuario/<int:id>', methods=['POST'])
@login_required
@admin_required
def atualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    usuario.nome = request.form['nome']
    usuario.tipo = request.form['tipo']
    usuario.email = request.form['email']
    nova_senha = request.form['senha']
    if nova_senha:
        usuario.senha = nova_senha
    
    usuario.senha = request.form['senha']
    db.session.commit()
    return redirect(url_for('usuarios.listar_usuarios'))
