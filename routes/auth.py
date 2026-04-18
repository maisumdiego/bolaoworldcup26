from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            return f"<h1>Erro: O email {email} já está cadastrado!</h1>"
        
        hashed_password = generate_password_hash(password)
        # Usando password_hash exatamente como no seu banco
        new_user = User(name=name, email=email, phone=phone, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.index')) 
        
    return render_template('register.html')

# =====================================================================

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    # Verificando contra password_hash
    if user and check_password_hash(user.password_hash, password):
        if not user.is_approved:
            return "Erro: Cadastro aguardando aprovação."
        login_user(user)
        return redirect(url_for('main.index')) 
    else:
        return "<h1>Erro: E-mail ou senha incorretos!</h1>"

# =====================================================================

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 