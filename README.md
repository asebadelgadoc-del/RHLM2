# ChallengeMe — Fútbol chileno

Aplicación inicial funcional con Flask, SQLite, Flask-Login, CSRF y Tailwind CSS por CDN.

## Requisitos
- Python 3.10 o superior
- Bash o terminal
- Conexión a internet para cargar Tailwind CSS desde CDN

## Instalación en Bash

```bash
cd ChallengeMe
python -m venv venv
source venv/Scripts/activate
```

Si estás usando Git Bash en Windows, normalmente funciona `source venv/Scripts/activate`.
En Linux/macOS usa `source venv/bin/activate`.

Instala dependencias:

```bash
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y cambia `SECRET_KEY` por una clave larga y privada.

En Git Bash:

```bash
cp .env.example .env
```

## Crear administrador

Primero registra una cuenta normal desde la página web. Luego, con el servidor detenido, ejecuta:

```bash
flask --app run.py shell
```

En la consola interactiva de Python:

```python
from app import db
from app.models import User
u = User.query.filter_by(username="TU_USUARIO").first()
u.is_admin = True
db.session.commit()
exit()
```

Después inicia la aplicación:

```bash
python run.py
```

Abre http://127.0.0.1:5000

## Funcionalidades incluidas
- Registro, inicio y cierre de sesión.
- Contraseñas almacenadas con hash.
- Protección CSRF para formularios.
- Dashboard con puntos y rachas.
- Reto diario con cinco preguntas seleccionadas del banco.
- 100 XP por respuesta correcta.
- Un intento por usuario y fecha.
- Ranking global.
- Perfil e historial.
- Catálogo inicial de Primera División y Primera B.
- Panel administrador para agregar preguntas.

## Importante
- Los equipos y preguntas iniciales son datos de demostración. Verifica la exactitud de cualquier dato futbolístico antes de usarlo en una presentación pública.
- Las imágenes de escudos y camisetas no están incluidas. El catálogo está preparado para incorporar sus rutas o URLs autorizadas.
- La selección diaria se mantiene estable por fecha mientras el banco de preguntas no cambie. En una versión de producción conviene guardar el conjunto de preguntas del día en tablas propias.
- El reto usa la fecha local del servidor. Para desplegar en Chile configura la zona horaria del servidor a America/Santiago o adapta el código para usar una zona horaria explícita.
- Tailwind se carga desde CDN para facilitar el inicio. Para producción se recomienda instalar y compilar Tailwind.
- Antes de desplegar, usa una SECRET_KEY segura, HTTPS, una base de datos persistente y configura copias de seguridad.
