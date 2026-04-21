from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
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
            flash(f"O email {email} já está cadastrado!", "warning")
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, phone=phone, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Cadastro realizado! Aguarde a aprovação do administrador.", "success")
        return redirect(url_for('main.index'))
        
    return render_template('register.html')

# =====================================================================

@auth_bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        if not user.is_approved:
            flash("Seu cadastro ainda aguarda aprovação administrativa.", "warning")
            return redirect(url_for('main.index'))
        login_user(user)
        return redirect(url_for('main.index')) 
    else:
        flash("E-mail ou senha incorretos!", "error")
        return redirect(url_for('main.index'))

# =====================================================================

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 