from app import db, create_app
from app.models import Rating

app = create_app()

with app.app_context():
    Rating.__table__.drop(db.engine, checkfirst=True)

    Rating.__table__.create(db.engine)
