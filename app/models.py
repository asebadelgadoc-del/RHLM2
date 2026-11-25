
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


# ==========================================
# MODELO DE USUARIOS
# ==========================================

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    total_points = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    current_streak = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    best_streak = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    last_played = db.Column(
        db.Date,
        nullable=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ==========================================
# MODELO DE COMPETICIONES
# ==========================================

class Competition(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    teams = db.relationship(
        "Team",
        backref="competition",
        lazy=True
    )

    questions = db.relationship(
        "Question",
        backref="competition",
        lazy=True
    )


# ==========================================
# MODELO DE EQUIPOS
# ==========================================

class Team(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("competition.id"),
        nullable=False
    )

    crest_url = db.Column(
        db.String(500),
        default=""
    )

    home_kit_url = db.Column(
        db.String(500),
        default=""
    )

    away_kit_url = db.Column(
        db.String(500),
        default=""
    )


# ==========================================
# MODELO DE CATEGORIAS
# ==========================================

class Category(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(60),
        unique=True,
        nullable=False
    )


# ==========================================
# MODELO DE PREGUNTAS
# ==========================================

class Question(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    prompt = db.Column(
        db.String(500),
        nullable=False
    )

    image_url = db.Column(
        db.String(500),
        default=""
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id"),
        nullable=False
    )

    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("competition.id"),
        nullable=True
    )

    category = db.relationship("Category")

    options = db.relationship(
        "Option",
        backref="question",
        cascade="all, delete-orphan",
        lazy=True
    )


# ==========================================
# MODELO DE ALTERNATIVAS
# ==========================================

class Option(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    text = db.Column(
        db.String(250),
        nullable=False
    )

    is_correct = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("question.id"),
        nullable=False
    )


# ==========================================
# MODELO DE PARTICIPACIONES
# ==========================================

class Participation(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    challenge_date = db.Column(
        db.Date,
        nullable=False
    )

    points = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    completed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="participations"
    )

    answers = db.relationship(
        "Answer",
        backref="participation",
        lazy=True,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "challenge_date",
            name="unique_user_daily_attempt"
        ),
    )


# ==========================================
# MODELO DE RESPUESTAS
# ==========================================

class Answer(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    participation_id = db.Column(
        db.Integer,
        db.ForeignKey("participation.id"),
        nullable=False
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("question.id"),
        nullable=False
    )

    option_id = db.Column(
        db.Integer,
        db.ForeignKey("option.id"),
        nullable=False
    )

    is_correct = db.Column(
        db.Boolean,
        nullable=False
    )

    question = db.relationship("Question")

    option = db.relationship("Option")
