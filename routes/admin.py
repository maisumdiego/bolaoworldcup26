from werkzeug.security import generate_password_hash
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models import db, Game, Team, GroupStanding, User, Config
from .auth_utils import admin_required
from utils import atualizar_classificacao_grupos, automatizar_chaveamento, avancar_mata_mata

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# =====================================================================

@admin_bp.route('/resultados')
@admin_required
def admin_resultados():
    # ... (rest of the method)

# =====================================================================

@admin_bp.route('/usuarios')
@admin_required
def gerenciar_usuarios():
    usuarios = User.query.order_by(User.is_approved.asc(), User.id.desc()).all()
    auto_approve_config = Config.query.filter_by(key='AUTO_APPROVE').first()
    auto_approve = auto_approve_config.value.lower() == 'true' if auto_approve_config else False
    return render_template('admin_usuarios.html', usuarios=usuarios, auto_approve=auto_approve)

# =====================================================================

@admin_bp.route('/config/auto_approve', methods=['POST'])
@admin_required
def toggle_auto_approve():
    status = request.form.get('status') # 'true' ou 'false'
    config = Config.query.filter_by(key='AUTO_APPROVE').first()
    
    if not config:
        config = Config(key='AUTO_APPROVE', value='true')
        db.session.add(config)
    
    config.value = status
    db.session.commit()
    
    msg = "Aprovação automática ATIVADA!" if status == 'true' else "Aprovação automática DESATIVADA!"
    return jsonify({"status": "success", "message": msg})

# =====================================================================

@admin_bp.route('/usuarios/acao', methods=['POST'])
@admin_required
def acao_usuario():
    user_id = request.form.get('user_id')
    acao = request.form.get('acao')

    usuario = User.query.get(user_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuário não encontrado."})
    
    try:
        if acao == 'aprovar':
            usuario.is_approved = True
            db.session.commit()
            return jsonify({"status": "success", "message": "Usuário ativado!"})
        
        if acao == 'desativar':
            usuario.is_approved = False
            db.session.commit()
            return jsonify({"status": "success", "message": "Usuário desativado com sucesso."})
        
        if acao == 'editar':
            usuario.name = request.form.get('name')
            usuario.email = request.form.get('email')
            usuario.phone = request.form.get('phone')
            db.session.commit()
            return jsonify({"status": "success", "message": "Dados atualizados!"})
            
        if acao == 'resetar_senha':
            nova_senha = 'bolao2026'
            usuario.password_hash = generate_password_hash(nova_senha)
            db.session.commit()
            return jsonify({"status": "success", "message": f"Senha resetada para: {nova_senha}"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

# ===================================================================== 

@admin_bp.route('/init_grupos')
@admin_required
def init_grupos():
    if GroupStanding.query.first():
        return "Os grupos já foram inicializados!"

    times = Team.query.all()
    if not times:
        return "A tabela de times está vazia."

    letras_grupos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    
    for i, time in enumerate(times):
        indice = (i // 4) % len(letras_grupos)
        letra_do_grupo = letras_grupos[indice]

        novo_time_no_grupo = GroupStanding(
            group_name=letra_do_grupo,
            team_id=time.id
        )
        db.session.add(novo_time_no_grupo)

    db.session.commit()
    return "✅ SUCESSO! Grupos inicializados via painel administrativo."