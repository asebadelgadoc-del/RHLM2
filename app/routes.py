import random
from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from app import db
from app.models import User, Competition, Team, Category, Question, Option, Participation, Answer

main = Blueprint("main", __name__)

def daily_questions():
    # El mismo conjunto de preguntas se conserva durante el día.
    today = date.today()
    random.seed(today.isoformat())
    return Question.query.all()[:0] + random.sample(
        Question.query.all(), min(5, Question.query.count())
    )

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")

@main.route("/registro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 8 or "@" not in email:
            flash("Revisa los datos. El usuario debe tener 3 caracteres y la contraseña 8.", "error")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Ese usuario o correo ya está registrado.", "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("¡Cuenta creada! Ya puedes jugar.", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter(
            (func.lower(User.email) == identity.lower()) |
            (func.lower(User.username) == identity.lower())
        ).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Usuario/correo o contraseña incorrectos.", "error")
    return render_template("login.html")

@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@main.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    played = Participation.query.filter_by(user_id=current_user.id, challenge_date=today).first()
    recent = Participation.query.filter_by(user_id=current_user.id).order_by(Participation.challenge_date.desc()).limit(5).all()
    top_users = User.query.order_by(User.total_points.desc(), User.username.asc()).limit(5).all()
    return render_template("dashboard.html", played=played, recent=recent, top_users=top_users)

@main.route("/reto")
@login_required
def challenge():
    today = date.today()
    participation = Participation.query.filter_by(user_id=current_user.id, challenge_date=today).first()
    if participation:
        return render_template("result.html", participation=participation)
    questions = daily_questions()
    return render_template("challenge.html", questions=questions)

@main.route("/responder", methods=["POST"])
@login_required
def submit_answers():
    today = date.today()
    if Participation.query.filter_by(user_id=current_user.id, challenge_date=today).first():
        flash("Ya completaste el reto de hoy.", "error")
        return redirect(url_for("main.dashboard"))

    questions = daily_questions()
    if not questions:
        flash("Todavía no hay preguntas disponibles.", "error")
        return redirect(url_for("main.dashboard"))

    points = 0
    answer_rows = []
    for question in questions:
        selected_id = request.form.get(f"question_{question.id}", type=int)
        option = Option.query.filter_by(id=selected_id, question_id=question.id).first()
        if not option:
            flash("Debes responder todas las preguntas.", "error")
            return redirect(url_for("main.challenge"))
        correct = bool(option.is_correct)
        if correct:
            points += 100
        answer_rows.append((question, option, correct))

    participation = Participation(user_id=current_user.id, challenge_date=today, points=points)
    db.session.add(participation)
    db.session.flush()
    for question, option, correct in answer_rows:
        db.session.add(Answer(
            participation_id=participation.id,
            question_id=question.id,
            option_id=option.id,
            is_correct=correct
        ))

    current_user.total_points += points
    if current_user.last_played == today - timedelta(days=1):
        current_user.current_streak += 1
    elif current_user.last_played != today:
        current_user.current_streak = 1
    current_user.best_streak = max(current_user.best_streak, current_user.current_streak)
    current_user.last_played = today
    db.session.commit()
    return render_template("result.html", participation=participation)

@main.route("/ranking")
@login_required
def ranking():
    users = User.query.order_by(User.total_points.desc(), User.username.asc()).all()
    return render_template("ranking.html", users=users)

@main.route("/equipos")
@login_required
def teams():
    competitions = Competition.query.all()
    return render_template("teams.html", competitions=competitions)

@main.route("/perfil")
@login_required
def profile():
    history = Participation.query.filter_by(user_id=current_user.id).order_by(Participation.challenge_date.desc()).all()
    return render_template("profile.html", history=history)

@main.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    categories = Category.query.order_by(Category.name).all()
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        category_id = request.form.get("category_id", type=int)
        choices = [request.form.get(f"option_{i}", "").strip() for i in range(1, 5)]
        correct = request.form.get("correct", type=int)
        category = db.session.get(Category, category_id)
        if not prompt or not category or any(not c for c in choices) or correct not in range(1, 5):
            flash("Completa la pregunta, categoría y las cuatro alternativas.", "error")
        else:
            question = Question(prompt=prompt, category=category)
            db.session.add(question)
            db.session.flush()
            for i, choice in enumerate(choices, start=1):
                db.session.add(Option(text=choice, is_correct=(i == correct), question=question))
            db.session.commit()
            flash("Pregunta agregada al banco de preguntas.", "success")
            return redirect(url_for("main.admin"))
    return render_template("admin.html", categories=categories, question_count=Question.query.count())

@main.app_errorhandler(403)
def forbidden(error):
    return render_template("error.html", message="No tienes permiso para entrar a esta sección."), 403

@main.app_errorhandler(404)
def not_found(error):
    return render_template("error.html", message="No encontramos esa página."), 404
