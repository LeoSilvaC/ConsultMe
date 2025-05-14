from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from .models import Consulta
from . import db
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
            return render_template('acesso_negado.html')
        return f(*args, **kwargs)
    return decorated_function


@consultas_bp.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso.")
    return redirect(url_for('auth.efetua_login'))


#Rota do formulário para criação de uma nova consulta
@consultas_bp.route('/cadastra_consulta')
@login_required
@admin_required
def exibe_formulario():
    return render_template('consultas/cadastra_consulta.html')

#Rota que faz o processo de receber e adicionar uma nova consulta 
@consultas_bp.route('/consultas', methods=['POST'])
@login_required
@admin_required
def cadastra_consulta():
    nome = request.form['nome']
    especialidade = request.form['especialidade']
    data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
    hora = request.form['hora']
    email = request.form['email']
    
    nova_consulta = Consulta(
        nome = nome,
        especialidade = especialidade,
        data = data,
        hora = hora,
        email = email
        )
    
    db.session.add(nova_consulta)
    db.session.commit()
    flash('Consulta cadastrada com sucesso!')
    return redirect(url_for('consultas.listar_consultas'))
    
#Rota que lista as consultas agendadas
@consultas_bp.route('/listar_consultas', methods=['GET'])
@login_required
def listar_consultas():
    nome = request.args.get('nome')
    data = request.args.get('data')
    consultas = Consulta.query  
    
    if nome:
        nome.lower()
        consultas = consultas.filter(func.lower(Consulta.nome).like(f"%{nome.lower()}%"))

    if data:
        consultas = consultas.filter(func.date(Consulta.data) == data)
        
    consultas = consultas.all()
    
    today = datetime.today().date()  
    consultas.sort(key=lambda c: abs((c.data - today).days))

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
    flash('Cadastro editado com sucesso')
    return redirect(url_for('consultas.listar_consultas'))
