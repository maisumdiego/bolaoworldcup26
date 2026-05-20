# Deploy Trigger: 2026-05-20
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

# CONFIGURAÇÕES GERAIS - Last Deploy Trigger: 2026-05-20
db_url = getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
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
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = 'info'
login_manager.login_view = 'main.index'
login_manager.init_app(app)


## Rota do login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# REGISTRO DOS MÓDULOS (BLUEPRINTS)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)

# INICIALIZAÇÃO AUTOMÁTICA (CRIAÇÃO DE TABELAS E CONFIGS)
with app.app_context():
    from models import Config
    db.create_all()
    # Garante que a configuração de aprovação automática exista
    if not Config.query.filter_by(key='AUTO_APPROVE').first():
        db.session.add(Config(
            key='AUTO_APPROVE', 
            value='true', 
            description='Aprovação automática de novos usuários'
        ))
        db.session.commit()

@app.context_processor
def inject_admin():
    return dict(admin_email=getenv('EMAIL_ADMIN'))

@app.context_processor
def inject_utils():
    return dict(calcular_pontos_palpite=calcular_pontos_palpite)


if __name__ == '__main__':
    app.run(debug=True)