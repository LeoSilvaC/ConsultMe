from app import create_app, db
from app.models import Usuario

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin_existente = Usuario.query.filter_by(email='admin@admin').first()
        if not admin_existente:
            admin = Usuario(
                nome='admin',
                email='admin@admin',
                senha='admin',
                tipo='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Administrador padrão criado: admin@admin / admin")
    app.run(debug=True)
    