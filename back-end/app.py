from datetime import datetime
from flask import Flask,request,render_template,url_for,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from sqlalchemy import  and_, func

app = Flask(__name__)
app.secret_key = 'consultme-projeto'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///consultas.db'
db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Você precisa estar logado para acessar esta página.")
            return redirect(url_for('efetua_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tipo = session.get('usuario_tipo')
        if tipo is None or tipo.lower() != 'administrador':
            flash("Somente administrador tem acesso a esta página!")
            return redirect(url_for('efetua_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso.")
    return redirect(url_for('efetua_login'))

#Criação de consulta no Banco de Dados
class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255))
    especialidade = db.Column(db.String(40))
    data = db.Column(db.Date)
    hora = db.Column(db.Integer)
    email = db.Column(db.String(100))

#Rota do formulário para criação de uma nova consulta
@app.route('/cadastra_consulta')
@login_required
def exibe_formulario():
    return render_template('cadastra_consulta.html')

#Rota que faz o processo de receber e adicionar uma nova consulta 
@app.route('/consultas', methods=['POST'])
@login_required
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
    return redirect(url_for('listar_consultas'))
    
#Rota que lista as consultas agendadas
@app.route('/listar_consultas', methods=['GET'])
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

    return render_template('listar_consultas.html', consultas=consultas)

#Rota que remove uma consulta
@app.route('/consultas/<int:id>', methods=['DELETE'])
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
@app.route('/editar_consulta/<int:id>')
@login_required
@admin_required
def editar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    return render_template('editar_consulta.html', consulta=consulta)

#Rota que atualiza a consulta editada
@app.route('/atualizar_consulta/<int:id>', methods=['POST'])
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
    return redirect(url_for('listar_consultas'))

##Criação de Usuários no Banco de Dados 
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'admin' ou 'usuario'

@app.route('/login', methods=['GET', 'POST'])
def efetua_login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        
        usuario_existe = Usuario.query.filter_by(email=email, senha=senha).first()
        
        if usuario_existe:
            session['usuario_id'] = usuario_existe.email
            session['usuario_tipo'] = usuario_existe.tipo
            return redirect(url_for('listar_consultas'))
        else:
            flash('Email/Senha está incorreto')
   
    return render_template('login.html')

@app.route('/cadastro', methods=['GET'])
@login_required
@admin_required
def exibe_formulario_usuario():
    return render_template('cadastra_usuario.html')

#Cadastro de novo usuario
@app.route('/cadastra_usuario', methods=["GET", "POST"])
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
            return redirect(url_for('efetua_login'))

    return render_template('cadastra_usuario.html')

@app.route('/listar_usuarios', methods=['GET'])
@login_required
@admin_required
def listar_usuarios():
    nome = request.args.get('nome')
    usuarios = Usuario.query  
    
    if nome:
        nome.lower()
        usuarios = usuarios.filter(func.lower(Usuario.nome).like(f"%{nome.lower()}%"))

    usuarios = usuarios.all()
    return render_template('listar_usuarios.html', usuarios=usuarios)

@app.route('/usuarios/<int:id>', methods=['DELETE'])
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
@app.route('/editar_usuario/<int:id>', methods=["GET"])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/atualizar_usuario/<int:id>', methods=['POST'])
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
    flash('Usuario editado com sucesso')
    return redirect(url_for('listar_usuarios'))

#Iniciar a Aplicação
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
