from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import current_user, login_required, logout_user
from .models import Consulta
from app.models import Usuario
from app import db
from datetime import datetime
from functools import wraps
from sqlalchemy import  and_, func

consultas_bp = Blueprint('consultas', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for('auth.efetua_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('usuario_tipo') != 'admin':
            return redirect(url_for('auth.acesso_negado'))
        return f(*args, **kwargs)
    return decorated_function

@consultas_bp.route('/logout')
def logout():
    logout_user()
    flash("Logout realizado com sucesso.")
    return redirect(url_for('auth.efetua_login'))


#Rota do formulário para criação de uma nova consulta
@consultas_bp.route('/cadastra_consulta', methods = ['GET'])
@login_required
@admin_required
def exibe_formulario():
    usuarios = Usuario.query.all()
    return render_template('consultas/cadastra_consulta.html', usuarios=usuarios)

#Rota que faz o processo de receber e adicionar uma nova consulta 
@consultas_bp.route('/consultas', methods=['POST'])
@login_required
@admin_required
def cadastra_consulta():
    
    usuario_id = request.form['usuario_id']
    especialidade = request.form['especialidade']
    data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
    hora = request.form['hora']
    email = request.form['email']
    
    nova_consulta = Consulta(
        nome = nome,
        usuario_id=usuario_id,
        especialidade = especialidade,
        data = data,
        hora = hora,
        email = email,
        )
    
    db.session.add(nova_consulta)
    db.session.commit()
    return redirect(url_for('consultas.listar_consultas'))
    
#Rota que lista as consultas agendadas
@consultas_bp.route('/listar_consultas', methods=['GET'])
@login_required
def listar_consultas():
    nome = request.args.get('nome')
    data = request.args.get('data')
    consultas = Consulta.query

    if current_user.tipo == 'admin':
            consultas = Consulta.query.all()
    else:
            consultas = Consulta.query.filter_by(usuario_id=current_user.id).all()

    return render_template('consultas/listar_consultas.html', consultas=consultas)

#Rota que remove uma consulta
@consultas_bp.route('/consultas/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def excluir_consulta(id):
    consulta = Consulta.query.get(id)
    
    if consulta:
        db.session.delete(consulta)
        db.session.commit()
        return {'mensagem': 'Consulta excluída com sucesso!'}
    else:
        return {'erro': 'Consulta não encontrada'}, 404

#Rota do formulário que edita uma consulta
@consultas_bp.route('/editar_consulta/<int:id>')
@login_required
@admin_required
def editar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    return render_template('consultas/editar_consulta.html', consulta=consulta)

#Rota que atualiza a consulta editada
@consultas_bp.route('/atualizar_consulta/<int:id>', methods=['POST'])
@login_required
@admin_required
def atualizar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    
    consulta.nome = request.form['nome']
    consulta.especialidade = request.form['especialidade']
    consulta.data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
    consulta.hora = request.form['hora']
    consulta.email = request.form['email']
    db.session.commit()
    return redirect(url_for('consultas.listar_consultas'))
