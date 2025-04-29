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

    #denormalised performance stats
    avg_time_sec = db.Column(db.Float, default=0)
    std_time_sec = db.Column(db.Float, default=0)  # standard deviation
    best_time_sec = db.Column(db.Float)
    best_question_id = db.Column(db.Integer, db.ForeignKey("question.title"))
    completed_questions = db.Column(db.Integer, default=0)
    completion_rate = db.Column(db.Float, default=0)  # percent (0-100)
    avg_attempts = db.Column(db.Float, default=0)

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

    #denormalised stats for quick access (updated after each submission)
    avg_time_sec = db.Column(db.Float, default=0)
    avg_tests = db.Column(db.Float, default=0)
    best_code_length = db.Column(db.Integer)
    completed_count = db.Column(db.Integer, default=0)

    #Relationships
    author_id = db.Column(db.Integer, db.ForeignKey("user.username", ondelete="SET NULL"))
    author = db.relationship("User", back_populates="questions")

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
    tags = db.relationship("Tag", secondary=question_tags, back_populates="question")

    def __repr__(self):
        return f"<Question {self.title}>"
    
class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    questions = db.relationship("Question", secondary=question_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"

class Submission(db.Model):
    __tablename__ = "submission"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.username", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(
        db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False
    )

    code = db.Column(db.Text, nullable=False)
    passed = db.Column(db.Boolean, nullable=False, default=False)
    runtime_sec = db.Column(db.Float)
    lines_of_code = db.Column(db.Integer)
    tests_run = db.Column(db.Integer)

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

    user_id = db.Column(db.Integer, db.ForeignKey("user.username", ondelete="CASCADE"), primary_key=True)
    question_id = db.Column(
        db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), primary_key=True
    )
    score = db.Column(db.Integer, nullable=False)  # 1‑5

    #Relationships
    user = db.relationship("User", back_populates="ratings")
    question = db.relationship("Question", back_populates="ratings")

    def __repr__(self):
        return f"<Rating {self.score} for c{self.question_id} by u{self.user_id}>"