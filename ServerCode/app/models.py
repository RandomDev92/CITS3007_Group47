from app import db

class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    