from app import create_app, db
from app.models import Service

app = create_app()
with app.app_context():
    services = Service.query.all()
    for s in services:
        if s.image and s.image.endswith('.jpg'):
            s.image = s.image[:-4] + '.png'
    db.session.commit()
    print("All Service.image fields updated to .png")
# Moved from project root to scripts/ as part of cleanup.
