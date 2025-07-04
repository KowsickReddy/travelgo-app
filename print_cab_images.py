from app import create_app, db
from app.models import Service

app = create_app()
with app.app_context():
    cabs = Service.query.filter(Service.category=='cab').all()
    for s in cabs:
        print(f"Service: {s.name}, Image: {s.image}")
