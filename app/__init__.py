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
    """Carga clubes y preguntas de ejemplo de forma idempotente."""
    from app.models import Competition, Category, Team, Question, Option

    competitions = {}
    for name in ("Primera División", "Primera B", "Segunda División Profesional"):
        competition = Competition.query.filter_by(name=name).first()
        if competition is None:
            competition = Competition(name=name)
            db.session.add(competition)
            db.session.flush()
        competitions[name] = competition

    teams_by_competition = {
        "Primera División": [
            "Audax Italiano", "Cobresal", "Colo-Colo", "Coquimbo Unido",
            "Deportes Concepción", "Deportes La Serena", "Deportes Limache",
            "Everton", "Huachipato", "Ñublense", "O'Higgins", "Palestino",
            "Unión La Calera", "Universidad Católica", "Universidad de Chile",
            "Universidad de Concepción",
        ],
        "Primera B": [
            "Cobreloa", "Curicó Unido", "Deportes Antofagasta", "Deportes Copiapó",
            "Deportes Iquique", "Deportes Puerto Montt", "Deportes Recoleta",
            "Deportes Santa Cruz", "Deportes Temuco", "Magallanes", "Rangers",
            "San Luis de Quillota", "San Marcos de Arica", "Santiago Wanderers",
            "Unión Española", "Unión San Felipe",
        ],
        "Segunda División Profesional": [
            "Atlético Colina", "Brujas de Salamanca", "Concón National",
            "Deportes Colchagua", "Deportes Linares", "Deportes Rengo",
            "General Velásquez", "Lota Schwager", "Provincial Ovalle",
            "Provincial Osorno", "Real San Joaquín", "Santiago City",
            "Santiago Morning", "Trasandino",
        ],
    }
    for competition_name, names in teams_by_competition.items():
        competition = competitions[competition_name]
        existing = {team.name.lower() for team in Team.query.filter_by(competition_id=competition.id).all()}
        for name in names:
            if name.lower() not in existing:
                db.session.add(Team(name=name, competition=competition))

    category_names = ["Historia", "Actualidad", "Estadísticas", "Clubes", "Jugadores", "Reglas", "Fútbol internacional"]
    categories = {}
    for name in category_names:
        category = Category.query.filter_by(name=name).first()
        if category is None:
            category = Category(name=name)
            db.session.add(category)
            db.session.flush()
        categories[name] = category

    # Cada pregunta incluye cuatro alternativas y el índice de la correcta (desde cero).
    questions = [
        ("Historia", "¿En qué año se fundó Colo-Colo?", ["1925", "1933", "1917", "1940"], 0),
        ("Clubes", "¿Qué club es conocido como Los Cruzados?", ["Colo-Colo", "Universidad Católica", "Cobreloa", "Huachipato"], 1),
        ("Clubes", "¿Qué equipo tiene como apodo Los Zorros del Desierto?", ["Cobreloa", "Everton", "O'Higgins", "Palestino"], 0),
        ("Historia", "¿En qué ciudad juega como local Deportes Temuco?", ["Valdivia", "Temuco", "Concepción", "Talca"], 1),
        ("Jugadores", "¿Qué posición corresponde principalmente a un arquero?", ["Defensa", "Volante", "Portero", "Delantero"], 2),
        ("Estadísticas", "¿Cuántos puntos se otorgan normalmente por una victoria en una liga?", ["1", "2", "3", "4"], 2),
        ("Clubes", "¿Qué colores se asocian tradicionalmente a Universidad de Chile?", ["Azul y rojo", "Azul y blanco", "Verde y blanco", "Negro y amarillo"], 0),
        ("Historia", "¿Qué organismo administra el fútbol profesional chileno?", ["ANFP", "COI", "CONMEBOL", "ATP"], 0),
        ("Estadísticas", "¿Qué dato indica los goles que ha marcado un equipo?", ["Goles a favor", "Tarjetas", "Corners recibidos", "Posesión rival"], 0),
        ("Estadísticas", "Si un equipo gana 2 partidos y empata 1, ¿cuántos puntos suma?", ["5", "6", "7", "4"], 0),
        ("Historia", "¿En qué año ganó Chile su primera Copa América masculina?", ["2015", "1991", "2016", "2007"], 0),
        ("Historia", "¿En qué año ganó Chile la Copa América Centenario?", ["2014", "2015", "2016", "2018"], 2),
        ("Fútbol internacional", "¿Qué selección ganó el Mundial de 2022?", ["Francia", "Argentina", "Brasil", "Croacia"], 1),
        ("Fútbol internacional", "¿Qué país ha ganado más Copas Mundiales masculinas?", ["Alemania", "Italia", "Brasil", "Argentina"], 2),
        ("Reglas", "¿Cuántos jugadores por equipo comienzan normalmente un partido?", ["9", "10", "11", "12"], 2),
        ("Reglas", "¿Cuánto dura un partido reglamentario sin contar descuentos ni prórroga?", ["80 minutos", "90 minutos", "100 minutos", "Dos tiempos de 45 minutos"], 1),
        ("Reglas", "¿Qué sanción recibe un jugador por una falta temeraria que amerita amonestación?", ["Tarjeta amarilla", "Tarjeta azul", "Expulsión automática", "Penal"], 0),
        ("Reglas", "¿Desde qué distancia se ejecuta un penal en el fútbol asociación?", ["9 metros", "10 metros", "11 metros", "12 metros"], 2),
        ("Jugadores", "¿Qué jugador es conocido como 'El Rey' y fue histórico mediocampista chileno?", ["Arturo Vidal", "Iván Zamorano", "Marcelo Salas", "Claudio Bravo"], 0),
        ("Jugadores", "¿En qué posición jugaba principalmente Marcelo Salas?", ["Arquero", "Delantero", "Defensa central", "Lateral"], 1),
        ("Clubes", "¿Qué club chileno juega tradicionalmente en el estadio San Carlos de Apoquindo, hoy Claro Arena?", ["Universidad Católica", "Audax Italiano", "Palestino", "Unión Española"], 0),
        ("Clubes", "¿Qué equipo es conocido como el Cacique?", ["Huachipato", "Colo-Colo", "Cobresal", "Rangers"], 1),
        ("Clubes", "¿Qué club tiene su sede en la ciudad de Talcahuano?", ["Huachipato", "O'Higgins", "Cobreloa", "Coquimbo Unido"], 0),
        ("Estadísticas", "¿Cómo se denomina marcar tres goles en un mismo partido?", ["Doblete", "Triplete", "Póker", "Hat-trick"], 3),
        ("Reglas", "¿Qué ocurre cuando un jugador recibe dos tarjetas amarillas en el mismo partido?", ["Sigue jugando", "Es expulsado", "Se repite el partido", "Se concede un penal"], 1),
        ("Fútbol internacional", "¿Qué organismo rige el fútbol mundial?", ["FIFA", "FIBA", "World Rugby", "COI"], 0),
        ("Fútbol internacional", "¿En qué país se originó la versión moderna del fútbol asociación?", ["Brasil", "Italia", "Inglaterra", "España"], 2),
        ("Historia", "¿Qué selección fue el rival de Chile en la final de la Copa América 2015?", ["Argentina", "Perú", "Uruguay", "México"], 0),
        ("Clubes", "¿Qué club chileno es conocido como los Mineros?", ["Cobresal", "Everton", "Palestino", "Ñublense"], 0),
        ("Jugadores", "¿Qué función caracteriza principalmente a un mediocampista?", ["Jugar solo como arquero", "Conectar defensa y ataque", "Cobrar siempre los penales", "Permanecer fuera de la cancha"], 1),
    ]

    existing_prompts = {q.prompt.strip().lower() for q in Question.query.all()}
    for category_name, prompt, choices, correct_index in questions:
        if prompt.strip().lower() in existing_prompts:
            continue
        question = Question(prompt=prompt, category=categories[category_name])
        db.session.add(question)
        db.session.flush()
        for index, choice in enumerate(choices):
            db.session.add(Option(text=choice, is_correct=(index == correct_index), question=question))
        existing_prompts.add(prompt.strip().lower())

    db.session.commit()
