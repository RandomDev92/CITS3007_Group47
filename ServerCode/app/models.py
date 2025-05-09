from datetime import datetime
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app import login_manager
import numpy as np

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class Difficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


question_tags = db.Table(
    "tags_associatioon",
    db.Column("question_id", db.Integer, db.ForeignKey("question.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


#user class
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)    
    password_hash = db.Column("password_hash", db.String(256), nullable=False)
    avatar_url = db.Column(db.String(512), default="mstom_400x400.jpg")
    share_profile = db.Column(db.Boolean, default=False)

    #denormalised performance stats
    avg_time_sec = db.Column(db.Float, default=0)
    std_time_sec = db.Column(db.Float, default=0)  # standard deviation
    best_time_sec = db.Column(db.Float, default=0)
    best_question_id = db.Column(db.Integer, db.ForeignKey("question.title"), nullable=True)
    completed_questions = db.Column(db.Integer, default=0)
    completion_rate = db.Column(db.Float, default=0)  # percent (0-100)
    avg_attempts = db.Column(db.Float, default=0)

    
    # Relationships
    questions = db.relationship(
        "Question",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="Question.author_id",
    )
    submissions = db.relationship(
        "Submission",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ratings = db.relationship(
        "Rating",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Password helpers
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # Repr
    def __repr__(self):
        return f"<User {self.id}>"
    
    def get_id(self):
        return self.id

class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    short_desc = db.Column(db.String(512), nullable=False)
    full_desc = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Enum(Difficulty), default=Difficulty.EASY, nullable=False)
    test_cases = db.Column(db.String(255))

    #denormalised stats for quick access (updated after each submission)
    avg_time_sec = db.Column(db.Float, default=0)
    avg_tests = db.Column(db.Float, default=0)
    best_code_length = db.Column(db.Integer)
    completed_count = db.Column(db.Integer, default=0)

    #Relationships
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    author = db.relationship("User", back_populates="questions", foreign_keys=[author_id], )

    submissions = db.relationship(
        "Submission",
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ratings = db.relationship(
        "Rating",
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags = db.relationship(
        'Tag',
        secondary=question_tags,
        backref=db.backref('question', lazy='dynamic'))
    
    def __repr__(self):
        return f"<Question {self.title}>"
    
class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    #questions = db.relationship("Question", secondary=question_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"

class Submission(db.Model):
    __tablename__ = "submission"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(
        db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False
    )

    code = db.Column(db.Text, nullable=False)
    passed = db.Column(db.Boolean, nullable=False, default=False)
    runtime_sec = db.Column(db.Float)
    lines_of_code = db.Column(db.Integer)
    total_attempts = db.Column(db.Integer)

    #Relationships
    user = db.relationship("User", back_populates="submissions")
    question = db.relationship("Question", back_populates="submissions")

    __table_args__ = (
        db.Index("ix_submission_user_question", "user_id", "question_id"),
    )

    def __repr__(self): 
        return f"<Submission u{self.user_id} c{self.question_id}>"

class Rating(db.Model):
    __tablename__ = "rating"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(
        db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), primary_key=True
    )
    score = db.Column(db.Integer, nullable=False)  # 1‑5

    #Relationships
    user = db.relationship("User", back_populates="ratings")
    question = db.relationship("Question", back_populates="ratings")

    def __repr__(self):
        return f"<Rating {self.score} for c{self.question_id} by u{self.user_id}>"

class ProfileShare(db.Model):
    __tablename__ = "profile_share"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    owner = db.relationship("User", foreign_keys=[owner_id], backref="shared_profiles")
    shared_with = db.relationship("User", foreign_keys=[shared_with_id], backref="received_profiles")