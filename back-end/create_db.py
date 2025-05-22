from app import app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    # Cria o admin se não existir
    if not Usuario.query.filter_by(email='admin@admin').first():
        admin = Usuario(
            nome='Administrador',
            email='admin@admin',
            senha=generate_password_hash('admin123'),
            tipo='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin criado com sucesso.")
    else:
        print("ℹ️ Admin já existe.")
