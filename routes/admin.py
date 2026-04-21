from werkzeug.security import generate_password_hash
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models import db, Game, Team, GroupStanding, User
from .auth_utils import admin_required
from utils import atualizar_classificacao_grupos, automatizar_chaveamento, avancar_mata_mata

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# =====================================================================

@admin_bp.route('/resultados')
@admin_required
def admin_resultados():
    
    jogos = Game.query.order_by(Game.datetime_game).all()
    
    jogos_por_fase = {}
    for jogo in jogos:
        if jogo.phase not in jogos_por_fase:
            jogos_por_fase[jogo.phase] = []
        jogos_por_fase[jogo.phase].append(jogo)
        
    fases_ordenadas = list(jogos_por_fase.keys())
    fase_ativa = fases_ordenadas[0] if fases_ordenadas else None
    
    todos_times = Team.query.order_by(Team.team_name).all()
    
    jogos_pendentes = Game.query.filter(
        (Game.phase != 'Grupos') & 
        ((Game.team_a_id == None) | (Game.team_b_id == None)) &
        ((Game.placeholder_a.ilike('%definir%')) | (Game.placeholder_b.ilike('%definir%')))
    ).order_by(Game.id).all()

    return render_template('admin_resultados.html',
                           jogos_por_fase=jogos_por_fase,
                           fases_ordenadas=fases_ordenadas,
                           fase_ativa=fase_ativa,
                           todos_times=todos_times, 
                           jogos_pendentes=jogos_pendentes)

# =====================================================================

@admin_bp.route('/salvar_resultado', methods=['POST'])
@admin_required
def salvar_resultado():
    game_id = request.form.get('game_id')
    res_a = request.form.get('result_a')
    res_b = request.form.get('result_b')

    jogo = Game.query.get(game_id)
    if jogo:
        try:
            jogo.team_a_result = int(res_a)
            jogo.team_b_result = int(res_b)
            jogo.status = 'encerrado' 
            db.session.commit()
            
            if jogo.phase == 'Grupos':
                atualizar_classificacao_grupos()
                automatizar_chaveamento()
            else:
                avancar_mata_mata(jogo)
   
            return jsonify({"status": "success", "message": "Resultado Gravado"})
        except ValueError:
            return jsonify({"status": "error", "message": "Valores inválidos"})
            
    return jsonify({"status": "error", "message": "Jogo não encontrado"}), 404

# =====================================================================

@admin_bp.route('/salvar_pendente', methods=['POST'])
@admin_required
def salvar_pendente():
    game_id = request.form.get('game_id')
    team_a_id = request.form.get('team_a_id')
    team_b_id = request.form.get('team_b_id')
    
    jogo = Game.query.get(game_id)
    if not jogo:
        return jsonify({"status": "error", "message": "Jogo não encontrado."}), 404
        
    try:
        if team_a_id:
            jogo.team_a_id = team_a_id
        if team_b_id:
            jogo.team_b_id = team_b_id
            
        db.session.commit()
        return jsonify({"status": "success", "message": "Confronto atualizado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# =====================================================================

@admin_bp.route('/usuarios')
@admin_required
def gerenciar_usuarios():
    usuarios = User.query.order_by(User.is_approved.asc(), User.id.desc()).all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

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