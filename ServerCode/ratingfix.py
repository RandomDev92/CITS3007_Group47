from app import db, create_app
from app.models import Rating, Tag
from app.SetupTags import createTags

def addTagsToExistingDB():
    for tag in createTags():
        if Tag.query.filter_by(name=tag).first() == None:
            t = Tag(name=tag)
            db.session.add(t)
    db.session.commit()

    

app = create_app()

with app.app_context():
    Rating.__table__.drop(db.engine, checkfirst=True)

    Rating.__table__.create(db.engine)
    addTagsToExistingDB()
