from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from routes.admin import admin_bp
from routes.main import main_bp
from routes.auth import auth_bp
from datetime import timedelta
import os

# IMPORTAÇÃO DOS NOSSOS MODELOS
from models import db, User

#load_dotenv()
app = Flask(__name__)

uri = os.getenv('DATABASE_URL')

if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

print("DATABASE_URL:", os.getenv('DATABASE_URL'))

# CONFIGURAÇÕES GERAIS
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)
app.config['SESSION_PERMANENT'] = False

# INICIALIZA O BANCO DE DADOS
db.init_app(app)

# INICIALIZA O LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

## Rota do login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# REGISTRO DOS MÓDULOS (BLUEPRINTS)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)

@app.context_processor
def inject_admin():
    return dict(admin_email=os.getenv('EMAIL_ADMIN'))


if __name__ == '__main__':
    app.run(debug=True)
