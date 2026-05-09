from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from collections import defaultdict
from datetime import datetime, timedelta
from collections import defaultdict
from models import db, Game, Prediction, User, GroupStanding, Team
from utils import calcular_pontos_palpite

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    brasil = Team.query.filter(Team.team_name.ilike('Brasil')).first()
    outros_times = Team.query.filter(Team.team_name.notilike('Brasil')).order_by(Team.team_name.asc()).all()
    todos_participantes = ([brasil] if brasil else []) + outros_times

    proximos_jogos = []
    palpites_usuario = {}
    
    if current_user.is_authenticated:
        agora = datetime.now()
        proximos_jogos = Game.query.filter(
            Game.datetime_game > agora, 
            Game.status != 'encerrado'
        ).order_by(Game.datetime_game.asc()).limit(4).all()
        
        ids_jogos = [j.id for j in proximos_jogos]
        if ids_jogos:
            palpites_raw = Prediction.query.filter(
                Prediction.user_id == current_user.id, 
                Prediction.game_id.in_(ids_jogos)
            ).all()
            palpites_usuario = {p.game_id: True for p in palpites_raw}

    return render_template('index.html', 
                           participantes=todos_participantes,
                           proximos_jogos=proximos_jogos,
                           palpites_usuario=palpites_usuario)

# =====================================================================

@main_bp.route('/palpites')
@login_required
def palpites():
    jogos = Game.query.order_by(Game.datetime_game).all()
    
    datas_existentes = set()
    grupos_existentes = set()
    fases_existentes = set()
    
    ordem_fases = ['Grupos', 'Segunda Rodada', 'Oitavas de Final', 'Quartas de Final', 'Semifinais', 'Terceiro Lugar', 'Final']

    for jogo in jogos:
        dia_str = jogo.datetime_game.strftime('%Y-%m-%d')
        datas_existentes.add(dia_str)
        
        grupo = ""
        if jogo.phase == 'Grupos':
            for team in [jogo.team_a, jogo.team_b]:
                if team:
                    if getattr(team, 'group_team', None): grupo = team.group_team
                    elif getattr(team, 'group', None): grupo = team.group
                    elif getattr(team, 'grupo', None): grupo = team.grupo
                    if grupo: break
        
        fase = jogo.phase
        if fase:
            fases_existentes.add(fase)

        jogo.dia_str = dia_str
        jogo.grupo_str = grupo
        jogo.fase_str = fase
        
        if grupo:
            grupos_existentes.add(grupo)
            
    datas_ordenadas = sorted(list(datas_existentes))
    grupos_ordenados = sorted(list(grupos_existentes))
    fases_ordenadas = [f for f in ordem_fases if f in fases_existentes]
    
    hoje = datetime.now().strftime('%Y-%m-%d')
    dia_ativo = hoje if hoje in datas_ordenadas else (datas_ordenadas[0] if datas_ordenadas else None)
    grupo_ativo = grupos_ordenados[0] if grupos_ordenados else None
    fase_ativa = fases_ordenadas[0] if fases_ordenadas else None

    nomes_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    dias_semana = {}
    for d in datas_ordenadas:
        data_obj = datetime.strptime(d, '%Y-%m-%d')
        dias_semana[d] = nomes_dias[data_obj.weekday()]

    palpites_raw = Prediction.query.filter_by(user_id=current_user.id).all()
    palpites_usuario = {p.game_id: {'a': p.result_a, 'b': p.result_b} for p in palpites_raw}

    return render_template('palpites.html', 
                           jogos=jogos, 
                           datas_ordenadas=datas_ordenadas,
                           dias_semana=dias_semana, 
                           grupos_ordenados=grupos_ordenados,
                           fases_ordenadas=fases_ordenadas,
                           dia_ativo=dia_ativo,
                           grupo_ativo=grupo_ativo,
                           fase_ativa=fase_ativa,
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
    if not jogo: return jsonify({"status": "error", "message": "Jogo não encontrado."}), 404
    if jogo.status == 'encerrado': return jsonify({"status": "error", "message": "Este jogo já foi encerrado."}), 403
    
    agora = datetime.now()
    limite_palpite = jogo.datetime_game - timedelta(minutes=10)

    if agora >= limite_palpite: return jsonify({"status": "error", "message": "Tempo esgotado para este jogo."}), 403
    
    try:
        novo_palpite = Prediction(user_id=current_user.id, game_id=jogo.id, result_a=int(result_a), result_b=int(result_b))
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
        pontos_totais = acertos_exatos = acertos_parciais = acertos_tendencia = 0
        
        palpites_raw = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()

        palpites_finais = {}
        for p in palpites_raw:
            if p.game_id not in palpites_finais:
                palpites_finais[p.game_id] = p

        for jogo in jogos_encerrados:
            palpite = palpites_finais.get(jogo.id)
            if palpite:
                pontos, tipo = calcular_pontos_palpite(
                    palpite.result_a, palpite.result_b, 
                    jogo.team_a_result, jogo.team_b_result
                )
                pontos_totais += pontos
                if tipo == 'exato': acertos_exatos += 1
                elif tipo == 'parcial': acertos_parciais += 1
                elif tipo == 'tendencia': acertos_tendencia += 1
                
        ranking_data.append({
            'nome': user.name, 
            'pontos': pontos_totais, 
            'exatos': acertos_exatos,
            'parciais': acertos_parciais, 
            'tendencia': acertos_tendencia,
            'profile_pic': user.profile_pic 
        })
    
    ranking_data.sort(key=lambda x: (x['pontos'], x['exatos'], x['parciais'], x['tendencia']), reverse=True)
    return render_template('ranking.html', ranking=ranking_data)

# =====================================================================

@main_bp.route('/torneio')
def torneio():
    standings = GroupStanding.query.all()
    grupos_dict = defaultdict(list)
    for s in standings: grupos_dict[s.group_name].append(s)
    for g in grupos_dict: grupos_dict[g].sort(key=lambda x: (x.points, x.goal_difference, x.goals_for), reverse=True)
    grupos_ordenados = dict(sorted(grupos_dict.items()))

    jogos_mata_mata_obj = Game.query.filter(Game.phase != 'Grupos').order_by(Game.id).all()
    
    ids_classificados = set()
    for j in jogos_mata_mata_obj:
        if j.team_a_id: ids_classificados.add(j.team_a_id)
        if j.team_b_id: ids_classificados.add(j.team_b_id)
    
    jogos_json = [{
        'id': j.id, 'phase': j.phase,
        'team_a_name': j.team_a.ab if j.team_a else j.placeholder_a,
        'team_b_name': j.team_b.ab if j.team_b else j.placeholder_b,
        'team_a_flag': j.team_a.team_flag_url if j.team_a else None,
        'team_b_flag': j.team_b.team_flag_url if j.team_b else None,
        'score_a': j.team_a_result if j.status == 'encerrado' else None,
        'score_b': j.team_b_result if j.status == 'encerrado' else None
    } for j in jogos_mata_mata_obj]
        
    return render_template('torneio.html', 
                           grupos=grupos_ordenados, 
                           jogos_mata_mata=jogos_json,
                           ids_classificados=list(ids_classificados))

# =====================================================================

@main_bp.route('/get_palpites_jogo/<int:jogo_id>')
@login_required
def get_palpites_jogo(jogo_id):
    jogo = Game.query.get_or_404(jogo_id)
    agora = datetime.now()
    visibilidade_liberada = (jogo.status == 'encerrado') or (agora >= (jogo.datetime_game - timedelta(minutes=10)))
    palpites_all = Prediction.query.filter_by(game_id=jogo_id).order_by(Prediction.created_at.desc()).all()
    
    ultimos_palpites = {}
    for p in palpites_all:
        if p.user_id not in ultimos_palpites:
            user = User.query.get(p.user_id)
            nome_usuario = user.name if user else "Anônimo"
            
            if visibilidade_liberada:
                pontos = 0
                if jogo.status == 'encerrado':
                    pontos, _ = calcular_pontos_palpite(
                        p.result_a, p.result_b, 
                        jogo.team_a_result, jogo.team_b_result
                    )
                ultimos_palpites[p.user_id] = {"nome": nome_usuario, "result_a": p.result_a, "result_b": p.result_b, "pontos": pontos, "liberado": True}
            else:
                ultimos_palpites[p.user_id] = {"nome": nome_usuario, "liberado": False}
        
    return jsonify({"status": "success", "visibilidade_liberada": visibilidade_liberada, "palpites": list(ultimos_palpites.values())})

@main_bp.route('/perfil')
@login_required
def perfil():
    jogos_encerrados = Game.query.filter_by(status='encerrado').order_by(Game.datetime_game).all()
    todos_usuarios = User.query.filter_by(is_approved=True).all()
    n_usuarios = len(todos_usuarios) if todos_usuarios else 1

    palpites_raw = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    
    palpites_finais_user = {}
    for p in palpites_raw:
        if p.game_id not in palpites_finais_user:
            palpites_finais_user[p.game_id] = p
            
    num_trocas = len(palpites_raw) - len(palpites_finais_user)
    
    ids_jogos = [j.id for j in jogos_encerrados]
    todos_palpites = Prediction.query.filter(Prediction.game_id.in_(ids_jogos)).order_by(Prediction.created_at.desc()).all()
    
    mapa_geral = defaultdict(dict)
    for p in todos_palpites:
        if p.user_id not in mapa_geral[p.game_id]:
            mapa_geral[p.game_id][p.user_id] = p

    stats = {'exatos': 0, 'parciais': 0, 'tendencia': 0, 'total_pontos': 0}
    user_evolucao, media_evolucao = defaultdict(int), defaultdict(float)
    historico = []

    for jogo in jogos_encerrados:
        dia = jogo.datetime_game.strftime('%d/%m')
        
        pts_grupo = 0
        for p_obj in mapa_geral[jogo.id].values():
            pts, _ = calcular_pontos_palpite(p_obj.result_a, p_obj.result_b, jogo.team_a_result, jogo.team_b_result)
            pts_grupo += pts
        media_evolucao[dia] += (pts_grupo / n_usuarios)

        p_u = palpites_finais_user.get(jogo.id)
        if p_u:
            pts_u, tipo = calcular_pontos_palpite(p_u.result_a, p_u.result_b, jogo.team_a_result, jogo.team_b_result)
            
            stats['total_pontos'] += pts_u
            if tipo == 'exato': stats['exatos'] += 1
            elif tipo == 'parcial': stats['parciais'] += 1
            elif tipo == 'tendencia': stats['tendencia'] += 1
            
            user_evolucao[dia] += pts_u

            historico.append({
                'timestamp': jogo.datetime_game.timestamp(),
                'data': jogo.datetime_game.strftime('%d/%m %H:%M'),
                'jogo': jogo,
                'palpite': f"{p_u.result_a} x {p_u.result_b}",
                'real': f"{jogo.team_a_result} x {jogo.team_b_result}",
                'pontos': pts_u,
                'tipo': tipo 
            })

    labels = sorted(list(set(user_evolucao.keys()) | set(media_evolucao.keys())))
    user_acc, media_acc, u_sum, m_sum = [], [], 0, 0
    for l in labels:
        u_sum += user_evolucao[l]; m_sum += media_evolucao[l]
        user_acc.append(u_sum); media_acc.append(round(m_sum, 1))

    return render_template('perfil.html', stats=stats, num_trocas=num_trocas, 
                           num_palpites=len(palpites_finais_user), total_jogos=len(jogos_encerrados),
                           chart_labels=labels, user_data=user_acc, media_data=media_acc, 
                           historico=historico)