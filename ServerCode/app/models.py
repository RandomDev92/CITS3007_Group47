from datetime import datetime
import enum

from . import db

class Difficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


question_tags = db.Table(
    "question_tags",
    db.Column("question_id", db.Integer, db.ForeignKey("questions.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


#user class
class User(db.Model):
    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    _password_hash = db.Column("password_hash", db.String(256), nullable=False)
    username = db.Column(db.String(64), primary_key=True, nullable=True)
    avatar_url = db.Column(db.String(512))
    share_profile = db.Column(db.Boolean, default=False)

    #relationships
    questions = db.relationship("Question", backref="author", lazy="dynamic")
    submissions = db.relationship("Submission", backref="user", lazy="dynamic")
    ratings = db.relationship("QuestionRating", backref="user", lazy="dynamic")

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    short_desc = db.Column(db.String(512))
    full_desc = db.Column(db.Text)
    difficulty = db.Column(db.Enum(Difficulty), default=Difficulty.EASY, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("users.username"))

    #relationships
    tags = db.relationship("Tag", secondary=question_tags, backref=db.backref("questions", lazy="dynamic"))
    test_cases = db.relationship("TestCase", backref="question", cascade="all, delete‑orphan", lazy="dynamic")
    submissions = db.relationship("Submission", backref="question", lazy="dynamic")
    ratings = db.relationship("QuestionRating", backref="question", lazy="dynamic")

