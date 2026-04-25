from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from routes.admin import admin_bp
from routes.main import main_bp
from routes.auth import auth_bp
from datetime import timedelta
import cloudinary
import cloudinary.uploader
from os import getenv
from utils import calcular_pontos_palpite


# IMPORTAÇÃO DOS NOSSOS MODELOS
from models import db, User

load_dotenv()
app = Flask(__name__)

# CONFIGURAÇÕES GERAIS
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)
app.config['SESSION_PERMANENT'] = False

cloudinary.config( 
  cloud_name = getenv('CLOUDINARY_CLOUD_NAME'), 
  api_key = getenv('CLOUDINARY_API_KEY'), 
  api_secret = getenv('CLOUDINARY_API_SECRET'),
  secure = True
)

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
    return dict(admin_email=getenv('EMAIL_ADMIN'))

@app.context_processor
def inject_utils():
    return dict(calcular_pontos_palpite=calcular_pontos_palpite)


if __name__ == '__main__':
    app.run(debug=True)