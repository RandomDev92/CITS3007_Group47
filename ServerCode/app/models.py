from app import db

#add the database stuff here

class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)

class Questions(db.Model):
    questionID = db.Column(db.Integer, primary_key=True)
    questionTitle = db.Column(db.String(50), nullable=False)
