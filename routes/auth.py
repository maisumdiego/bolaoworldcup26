import os  # <-- IMPORTANTE: Adicionado para ler as variáveis de ambiente
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User
from cloudinary.uploader import upload

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
        
        auto_approve = os.getenv('AUTO_APPROVE', 'False').lower() == 'true'

        hashed_password = generate_password_hash(password)
        
        new_user = User(
            name=name, 
            email=email, 
            phone=phone, 
            password_hash=hashed_password,
            is_approved=auto_approve
        )
        db.session.add(new_user)
        db.session.commit()

        if auto_approve:
            flash("Cadastro realizado com sucesso! Você já pode fazer login.", "success")
        else:
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


@auth_bp.route('/atualizar_perfil', methods=['POST'])
@login_required
def atualizar_perfil():
    name = request.form.get('name')
    nova_senha = request.form.get('password')
    foto = request.files.get('foto')

    if name:
        current_user.name = name
    
    if nova_senha and nova_senha.strip() != "":
        from werkzeug.security import generate_password_hash
        current_user.password = generate_password_hash(nova_senha)
        
    if foto and foto.filename != '':
        user_email_id = current_user.email.replace('@', '_at_').replace('.', '_')
        
        try:
            upload_result = upload(
                foto, 
                folder="bolao_profiles/", 
                public_id=user_email_id,
                overwrite=True,
                resource_type="image"
            )
            
            current_user.profile_pic = upload_result['secure_url']
        except Exception as e:
            print(f"Erro no Cloudinary: {e}")

    db.session.commit()
    return redirect(url_for('main.perfil'))