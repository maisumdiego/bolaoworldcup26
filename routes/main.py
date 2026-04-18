from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from collections import defaultdict
from models import db, Game, Prediction, User, GroupStanding, Team

main_bp = Blueprint('main', __name__)

# =====================================================================

@main_bp.route('/')
def index():
    return render_template('index.html')

# =====================================================================

@main_bp.route('/palpites')
@login_required
def palpites():
    jogos = Game.query.order_by(Game.datetime_game).all()
    
    jogos_por_dia = defaultdict(list)
    for jogo in jogos:
        dia_str = jogo.datetime_game.strftime('%Y-%m-%d')
        jogos_por_dia[dia_str].append(jogo)
        
    datas_ordenadas = sorted(jogos_por_dia.keys())
    hoje = datetime.now().strftime('%Y-%m-%d')
    dia_ativo = hoje if hoje in datas_ordenadas else (datas_ordenadas[0] if datas_ordenadas else None)

    palpites_raw = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()

    palpites_usuario = {}
    for p in palpites_raw:
        if p.game_id not in palpites_usuario:
            palpites_usuario[p.game_id] = {'a': p.result_a, 'b':p.result_b}

    return render_template('palpites.html', 
                           jogos_por_dia=jogos_por_dia, 
                           datas_ordenadas=datas_ordenadas, 
                           dia_ativo=dia_ativo,
                           agora=datetime.now(),
                           timedelta=timedelta,
                           palpites_usuario=palpites_usuario)

# =====================================================================

@main_bp.route('/salvar_palpite', methods=['POST'])
@login_required
def salvar_palpite():
    game_id = request.form.get('game_id')
    result_a = request.form.get('result_a')
    result_b = request.form.get('result_b')

    jogo = Game.query.get(game_id)
    if not jogo:
        return jsonify({"status": "error", "message": "Jogo não encontrado."}), 404
    
    if jogo.status == 'encerrado':
        return jsonify({"status": "error", "message": "Este jogo já foi encerrado e auditado."}), 403
    
    agora = datetime.now()
    limite_palpite = jogo.datetime_game - timedelta(minutes=10)

    if agora >= limite_palpite:
        return jsonify({"status": "error", "message": "Tempo esgotado para este jogo."}), 403
    
    try:
        novo_palpite = Prediction(
            user_id=current_user.id,
            game_id=jogo.id,
            result_a=int(result_a),
            result_b=int(result_b)
        )
        db.session.add(novo_palpite)
        db.session.commit()
        return jsonify({"status": "success", "message": "Salvo"}), 200
    except ValueError:
        return jsonify({"status": "error", "message": "Valores inválidos."}), 400

# =====================================================================

@main_bp.route('/ranking')
@login_required
def ranking():
    usuarios = User.query.filter_by(is_approved=True).all()
    jogos_encerrados = Game.query.filter_by(status='encerrado').all()

    ranking_data = []

    for user in usuarios:
        pontos_totais = 0
        acertos_exatos = 0
        acertos_parciais = 0
        acertos_tendencia = 0

        palpites_raw = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()

        palpites_finais = {}
        for p in palpites_raw:
            if p.game_id not in palpites_finais:
                palpites_finais[p.game_id] = p

        for jogo in jogos_encerrados:
            palpite = palpites_finais.get(jogo.id)
            if palpite:
                p_a = palpite.result_a
                p_b = palpite.result_b
                r_a = jogo.team_a_result
                r_b = jogo.team_b_result

                # Regra 1: Placar exato (5 pts)
                if p_a == r_a and p_b == r_b:
                    pontos_totais += 5
                    acertos_exatos += 1
                # Regra 2: Acertou a tendência (Vencedor ou Empate)
                elif (p_a > p_b and r_a > r_b) or (p_a < p_b and r_a < r_b) or (p_a == p_b and r_a == r_b):
                    # Acertou a tendência E acertou os gols de um dos times (3 pts)
                    if p_a == r_a or p_b == r_b:
                        pontos_totais += 3
                        acertos_parciais += 1
                    # Acertou só a tendência (2 pts)
                    else:
                        pontos_totais += 2
                        acertos_tendencia += 1
        
        ranking_data.append({
            'nome': user.name,
            'pontos': pontos_totais,
            'exatos': acertos_exatos,
            'parciais': acertos_parciais,
            'tendencia': acertos_tendencia
        })
    
    # 1º Pontos | 2º Exatos | 3º Parciais | 4º Tendência
    ranking_data.sort(key=lambda x: (x['pontos'], x['exatos'], x['parciais'], x['tendencia']), reverse=True)
    
    return render_template('ranking.html', ranking=ranking_data)

# =====================================================================

@main_bp.route('/init_grupos')
def init_grupos():
    if GroupStanding.query.first():
        return "Os grupos já foram inicializados antes! Verifique o banco de dados."

    times = Team.query.all()
    
    if not times:
        return "A tabela de times está vazia. Cadastre os times primeiro!"

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
    return "✅ SUCESSO! Tabela fact_group_standings populada. Volte para a rota /grupos e veja a mágica."

# =====================================================================

@main_bp.route('/torneio')
def torneio():
    # ==========================================
    # 1. DADOS DA FASE DE GRUPOS
    # ==========================================
    standings = GroupStanding.query.all()
    grupos_dict = defaultdict(list)
    for s in standings:
        grupos_dict[s.group_name].append(s)
        
    for g in grupos_dict:
        grupos_dict[g].sort(key=lambda x: (x.points, x.goal_difference, x.goals_for), reverse=True)
        
    grupos_ordenados = dict(sorted(grupos_dict.items()))

    # ==========================================
    # 2. DADOS DO MATA-MATA (CHAVEAMENTO)
    # ==========================================
    jogos_mata_mata = Game.query.filter(Game.phase != 'Grupos').order_by(Game.id).all()
    
    jogos_json = []
    for jogo in jogos_mata_mata:
        jogos_json.append({
            'id': jogo.id,
            'phase': jogo.phase,
            'team_a_name': jogo.team_a.ab if jogo.team_a else jogo.placeholder_a,
            'team_b_name': jogo.team_b.ab if jogo.team_b else jogo.placeholder_b,
            'team_a_flag': jogo.team_a.team_flag_url if jogo.team_a else None,
            'team_b_flag': jogo.team_b.team_flag_url if jogo.team_b else None,
            'score_a': jogo.team_a_result if jogo.status == 'encerrado' else None,
            'score_b': jogo.team_b_result if jogo.status == 'encerrado' else None
        })
        
    # Enviamos TUDO para uma única tela
    return render_template('torneio.html', grupos=grupos_ordenados, jogos_mata_mata=jogos_json)