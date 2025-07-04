from app import create_app, db
from app.models import Service

app = create_app()
app.app_context().push()

# Sample data for each category
# Moved from project root to scripts/ as part of cleanup.
