import os
from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///challengeme.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Inicia sesión para continuar."

    from app.models import User
    from app.routes import main
    app.register_blueprint(main)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()
        seed_demo_data()

    return app

def seed_demo_data():
    from app.models import Competition, Category, Team, Question, Option

    if Competition.query.first():
        return

    primera = Competition(name="Primera División")
    primera_b = Competition(name="Primera B")
    db.session.add_all([primera, primera_b])
    db.session.flush()

    categories = [
        Category(name="Historia"),
        Category(name="Actualidad"),
        Category(name="Estadísticas"),
        Category(name="Clubes"),
        Category(name="Jugadores"),
    ]
    db.session.add_all(categories)
    db.session.flush()

    teams = [
        Team(name="Colo-Colo", competition=primera, crest_url=""),
        Team(name="Universidad de Chile", competition=primera, crest_url=""),
        Team(name="Universidad Católica", competition=primera, crest_url=""),
        Team(name="Cobreloa", competition=primera_b, crest_url=""),
        Team(name="Deportes Temuco", competition=primera_b, crest_url=""),
    ]
    db.session.add_all(teams)
    db.session.flush()

    # Preguntas de demostración: revisa y amplía estos datos antes de publicar.
    demo_questions = [
        ("Historia", "¿En qué año se fundó Colo-Colo?", ["1925", "1933", "1917", "1940"], 0),
        ("Clubes", "¿Qué club es conocido como Los Cruzados?", ["Colo-Colo", "Universidad Católica", "Cobreloa", "Huachipato"], 1),
        ("Clubes", "¿Qué equipo tiene como apodo Los Zorros del Desierto?", ["Cobreloa", "Everton", "O'Higgins", "Palestino"], 0),
        ("Historia", "¿En qué ciudad juega como local Deportes Temuco?", ["Valdivia", "Temuco", "Concepción", "Talca"], 1),
        ("Jugadores", "¿Qué posición corresponde principalmente a un arquero?", ["Defensa", "Volante", "Portero", "Delantero"], 2),
        ("Estadísticas", "¿Cuántos puntos se otorgan normalmente por una victoria en una liga?", ["1", "2", "3", "4"], 2),
        ("Clubes", "¿Qué colores se asocian tradicionalmente a Universidad de Chile?", ["Azul y rojo", "Azul y blanco", "Verde y blanco", "Negro y amarillo"], 0),
        ("Historia", "¿Qué organismo organiza el fútbol profesional chileno?", ["ANFP", "FIFA Chile", "COI", "CONMEBOL local"], 0),
        ("Actualidad", "¿Qué dato permite saber cuántos goles ha marcado un equipo?", ["Goles a favor", "Tarjetas", "Corners recibidos", "Posesión rival"], 0),
        ("Estadísticas", "Si un equipo gana 2 partidos y empata 1, ¿cuántos puntos suma?", ["5", "6", "7", "4"], 0),
    ]

    category_map = {c.name: c for c in categories}
    for category_name, prompt, choices, correct_index in demo_questions:
        q = Question(prompt=prompt, category=category_map[category_name])
        db.session.add(q)
        db.session.flush()
        for index, choice in enumerate(choices):
            db.session.add(Option(
                text=choice, is_correct=(index == correct_index), question=q
            ))
    db.session.commit()
