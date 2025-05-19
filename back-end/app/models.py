from . import db

#Criação de consulta no Banco de Dados
class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    nome = db.Column(db.String(255))
    especialidade = db.Column(db.String(40))
    data = db.Column(db.Date)
    hora = db.Column(db.Integer)
    email = db.Column(db.String(100), nullable=False)
    usuario = db.relationship('Usuario', back_populates = 'consultas')


##Criação de Usuários no Banco de Dados 
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)

    consultas = db.relationship('Consulta', back_populates = 'usuario')