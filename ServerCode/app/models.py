from datetime import datetime
import enum
from werkzeug.security import generate_password_hash, check_password_hash


from app import db

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

    username = db.Column(db.String(64), primary_key=True, nullable=True)    
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    _password_hash = db.Column("password_hash", db.String(256), nullable=False)
    avatar_url = db.Column(db.String(512))
    share_profile = db.Column(db.Boolean, default=False)

    #relationships
    questions = db.relationship("Question", backref="author", lazy="dynamic")
    submissions = db.relationship("Submission", backref="user", lazy="dynamic")
    ratings = db.relationship("QuestionRating", backref="user", lazy="dynamic")

    # Relationships
    question = db.relationship(
        "Question",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
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
        return f"<User {self.display_name} ({self.email})>"

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    short_desc = db.Column(db.String(512))
    full_desc = db.Column(db.Text)
    difficulty = db.Column(db.Enum(Difficulty), default=Difficulty.EASY, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("users.username"))

    #denormalised stats for quick access (updated after each submission)
    avg_time_sec = db.Column(db.Float, default=0)
    avg_tests = db.Column(db.Float, default=0)
    best_code_length = db.Column(db.Integer)
    completed_count = db.Column(db.Integer, default=0)

    #Relationships
    author_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    author = db.relationship("User", back_populates="challenges")

    submissions = db.relationship(
        "Submission",
        back_populates="challenge",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ratings = db.relationship(
        "Rating",
        back_populates="challenge",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags = db.relationship("Tag", secondary=challenge_tags, back_populates="challenges")

    def __repr__(self):
        return f"<Challenge {self.title}>"
    
class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    challenges = db.relationship("Challenge", secondary=challenge_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"

