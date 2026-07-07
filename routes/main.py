from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from collections import defaultdict
from datetime import datetime, timedelta
from models import db, Game, Prediction, User, GroupStanding, Team
from utils import calcular_pontos_palpite, get_now

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    brasil = Team.query.filter(Team.team_name.ilike('Brasil')).first()
    outros_times = Team.query.filter(Team.team_name.notilike('Brasil')).order_by(Team.team_name.asc()).all()
    todos_participantes = ([brasil] if brasil else []) + outros_times

    proximos_jogos = []
    palpites_usuario = {}
    
    if current_user.is_authenticated:
        agora = get_now()
        proximos_jogos = Game.query.filter(
            Game.datetime_game > agora, 
            Game.status != 'encerrado'
        ).order_by(Game.datetime_game.asc()).limit(4).all()
        
        ids_jogos = [j.id for j in proximos_jogos]
        if ids_jogos:
            palpites_raw = Prediction.query.filter(
                Prediction.user_id == current_user.id, 
                Prediction.game_id.in_(ids_jogos)
            ).order_by(Prediction.created_at.asc()).all()
            palpites_usuario = {p.game_id: True for p in palpites_raw}

    return render_template('index.html', 
                           participantes=todos_participantes,
                           proximos_jogos=proximos_jogos,
                           palpites_usuario=palpites_usuario)

# =====================================================================

from sqlalchemy.orm import joinedload

@main_bp.route('/palpites')
@login_required
def palpites():
    # Usando joinedload para garantir que os times sejam carregados
    jogos = Game.query.options(joinedload(Game.team_a), joinedload(Game.team_b)).order_by(Game.datetime_game).all()
    
    datas_existentes = set()
    grupos_existentes = set()
    fases_existentes = set()
    
    ordem_fases = ['Grupos', '16 Avos de Final', 'Oitavas de Final', 'Quartas de Final', 'Semifinais', 'Terceiro Lugar', 'Final']

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
    
    hoje = get_now().strftime('%Y-%m-%d')
    dia_ativo = hoje if hoje in datas_ordenadas else (datas_ordenadas[0] if datas_ordenadas else None)
    grupo_ativo = grupos_ordenados[0] if grupos_ordenados else None
    fase_ativa = fases_ordenadas[0] if fases_ordenadas else None

    nomes_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    dias_semana = {}
    for d in datas_ordenadas:
        data_obj = datetime.strptime(d, '%Y-%m-%d')
        dias_semana[d] = nomes_dias[data_obj.weekday()]

    palpites_raw = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.asc()).all()
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
                           agora=get_now(),
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
    
    agora = get_now()
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
    agora = get_now()
    jogos_encerrados = Game.query.options(joinedload(Game.team_a), joinedload(Game.team_b)).filter(
        Game.status == 'encerrado',
        Game.datetime_game <= agora
    ).order_by(Game.datetime_game.desc(), Game.id.desc()).all()
    ranking_data = []

    ultimo_jogo = jogos_encerrados[0] if jogos_encerrados else None
    ultimo_jogo_str = ""
    jogo_simultaneo = None
    
    if ultimo_jogo:
        def url_to_emoji(url):
            if not url: return ""
            code = url.split('/')[-1].split('.')[0].upper()
            if len(code) == 2:
                return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)
            return ""

        t_a = ultimo_jogo.team_a.ab if ultimo_jogo.team_a else ultimo_jogo.placeholder_a
        t_b = ultimo_jogo.team_b.ab if ultimo_jogo.team_b else ultimo_jogo.placeholder_b
        emj_a = url_to_emoji(ultimo_jogo.team_a.team_flag_url) if getattr(ultimo_jogo, 'team_a', None) else ""
        emj_b = url_to_emoji(ultimo_jogo.team_b.team_flag_url) if getattr(ultimo_jogo, 'team_b', None) else ""
        
        r_a = ultimo_jogo.team_a_result
        r_b = ultimo_jogo.team_b_result
        ultimo_jogo_str = f"{emj_a} {t_a} {r_a} x {r_b} {t_b} {emj_b}".strip()
        
        # Check for simultaneous game
        jogo_simultaneo = Game.query.filter(
            Game.id != ultimo_jogo.id,
            Game.datetime_game == ultimo_jogo.datetime_game,
            Game.status == 'encerrado'
        ).first()
        
        if jogo_simultaneo:
            t_a_s = jogo_simultaneo.team_a.ab if getattr(jogo_simultaneo, 'team_a', None) else jogo_simultaneo.placeholder_a
            t_b_s = jogo_simultaneo.team_b.ab if getattr(jogo_simultaneo, 'team_b', None) else jogo_simultaneo.placeholder_b
            emj_a_s = url_to_emoji(jogo_simultaneo.team_a.team_flag_url) if getattr(jogo_simultaneo, 'team_a', None) else ""
            emj_b_s = url_to_emoji(jogo_simultaneo.team_b.team_flag_url) if getattr(jogo_simultaneo, 'team_b', None) else ""
            r_a_s = jogo_simultaneo.team_a_result
            r_b_s = jogo_simultaneo.team_b_result
            ultimo_jogo_str = f"_\\n_{ultimo_jogo_str}_\\n_{emj_a_s} {t_a_s} {r_a_s} x {r_b_s} {t_b_s} {emj_b_s}".strip()

    # Correção N+1: Buscar todos os palpites dos usuários aprovados de uma única vez
    ids_usuarios = [u.id for u in usuarios]
    todos_palpites_raw = Prediction.query.filter(Prediction.user_id.in_(ids_usuarios)).order_by(Prediction.created_at.desc()).all()
    
    palpites_por_usuario = defaultdict(list)
    for p in todos_palpites_raw:
        palpites_por_usuario[p.user_id].append(p)

    for user in usuarios:
        pontos_totais = acertos_exatos = acertos_parciais = acertos_tendencia = 0
        pontos_ultimo_jogo = 0
        
        # Agora busca na memória (dicionário) ao invés de bater no banco a cada loop
        palpites_raw = palpites_por_usuario[user.id]

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
                
                if ultimo_jogo and jogo.id == ultimo_jogo.id:
                    pontos_ultimo_jogo += pontos
                elif jogo_simultaneo and jogo.id == jogo_simultaneo.id:
                    pontos_ultimo_jogo += pontos
                
        ranking_data.append({
            'nome': user.name, 
            'pontos': pontos_totais, 
            'exatos': acertos_exatos,
            'parciais': acertos_parciais, 
            'tendencia': acertos_tendencia,
            'profile_pic': user.profile_pic,
            'pontos_ultimo': pontos_ultimo_jogo
        })
    
    # Ordenação: Pontos -> Exatos -> Parciais -> Tendência -> Nome (Alfabético)
    ranking_data.sort(key=lambda x: (
        -int(x['pontos']), 
        -int(x['exatos']), 
        -int(x['parciais']), 
        -int(x['tendencia']), 
        x['nome'].lower()
    ))
    
    # Atribuição de Colocação (Rank) com lógica de blocos
    if ranking_data:
        pos_atual = 1
        for i in range(len(ranking_data)):
            if i > 0:
                # Se as estatísticas de pontuação forem idênticas ao anterior, mantém o mesmo rank
                anterior = ranking_data[i-1]
                atual = ranking_data[i]
                if (atual['pontos'] == anterior['pontos'] and 
                    atual['exatos'] == anterior['exatos'] and 
                    atual['parciais'] == anterior['parciais'] and 
                    atual['tendencia'] == anterior['tendencia']):
                    pass # pos_atual continua a mesma
                else:
                    pos_atual += 1
            ranking_data[i]['rank'] = pos_atual
    
    return render_template('ranking.html', ranking=ranking_data, ultimo_jogo_str=ultimo_jogo_str)

# =====================================================================

@main_bp.route('/torneio')
def torneio():
    standings = GroupStanding.query.all()
    grupos_dict = defaultdict(list)
    for s in standings: grupos_dict[s.group_name].append(s)
    for g in grupos_dict: grupos_dict[g].sort(key=lambda x: (x.points, x.goal_difference, x.goals_for), reverse=True)
    grupos_ordenados = dict(sorted(grupos_dict.items()))

    jogos_mata_mata_obj = Game.query.options(joinedload(Game.team_a), joinedload(Game.team_b)).filter(Game.phase != 'Grupos').order_by(Game.id).all()
    
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
        'team_a_id': j.team_a_id,
        'team_b_id': j.team_b_id,
        'score_a': j.team_a_result if j.status == 'encerrado' else None,
        'score_b': j.team_b_result if j.status == 'encerrado' else None,
        'penalties_winner_id': getattr(j, 'penalties_winner_id', None)
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
    agora = get_now()
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
        
    jogo_simultaneo_data = None
    if jogo.phase == 'Grupos' and jogo.team_a and jogo.team_a.group_team:
        jogo_simultaneo = Game.query.join(Team, Game.team_a_id == Team.id).filter(
            Game.phase == 'Grupos',
            Game.datetime_game == jogo.datetime_game,
            Game.id != jogo.id,
            Team.group_team == jogo.team_a.group_team
        ).first()
        
        if jogo_simultaneo:
            jogo_simultaneo_data = {
                "time_a": jogo_simultaneo.team_a.team_name if jogo_simultaneo.team_a else jogo_simultaneo.placeholder_a,
                "time_b": jogo_simultaneo.team_b.team_name if jogo_simultaneo.team_b else jogo_simultaneo.placeholder_b,
                "iso_a": jogo_simultaneo.team_a.team_flag_url.split('/')[-1].split('.')[0] if jogo_simultaneo.team_a and jogo_simultaneo.team_a.team_flag_url else None,
                "iso_b": jogo_simultaneo.team_b.team_flag_url.split('/')[-1].split('.')[0] if jogo_simultaneo.team_b and jogo_simultaneo.team_b.team_flag_url else None,
                "placar_a": jogo_simultaneo.team_a_result,
                "placar_b": jogo_simultaneo.team_b_result
            }

    return jsonify({
        "status": "success", 
        "visibilidade_liberada": visibilidade_liberada, 
        "time_a": jogo.team_a.team_name if jogo.team_a else jogo.placeholder_a,
        "time_b": jogo.team_b.team_name if jogo.team_b else jogo.placeholder_b,
        "iso_a": jogo.team_a.team_flag_url.split('/')[-1].split('.')[0] if jogo.team_a and jogo.team_a.team_flag_url else None,
        "iso_b": jogo.team_b.team_flag_url.split('/')[-1].split('.')[0] if jogo.team_b and jogo.team_b.team_flag_url else None,
        "placar_a": jogo.team_a_result,
        "placar_b": jogo.team_b_result,
        "jogo_simultaneo": jogo_simultaneo_data,
        "data_hora": jogo.datetime_game.strftime('%d/%m - %H:%M'),
        "palpites": sorted(list(ultimos_palpites.values()), key=lambda x: x['nome'].lower())
    })

@main_bp.route('/get_historico_usuario/<string:nome_usuario>')
@login_required
def get_historico_usuario(nome_usuario):
    user = User.query.filter_by(name=nome_usuario).first_or_404()
    agora = get_now()
    jogos_encerrados = Game.query.options(joinedload(Game.team_a), joinedload(Game.team_b)).filter(
        Game.status == 'encerrado',
        Game.datetime_game <= agora
    ).order_by(Game.datetime_game.desc(), Game.id.desc()).all()
    
    palpites_raw = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()
    palpites_finais = {}
    for p in palpites_raw:
        if p.game_id not in palpites_finais:
            palpites_finais[p.game_id] = p
            
    historico = []
    for jogo in jogos_encerrados:
        p = palpites_finais.get(jogo.id)
        if p:
            pontos, tipo = calcular_pontos_palpite(
                p.result_a, p.result_b, 
                jogo.team_a_result, jogo.team_b_result
            )
            historico.append({
                'time_a': jogo.team_a.ab if jogo.team_a else jogo.placeholder_a,
                'time_b': jogo.team_b.ab if jogo.team_b else jogo.placeholder_b,
                'flag_a': jogo.team_a.team_flag_url if jogo.team_a else None,
                'flag_b': jogo.team_b.team_flag_url if jogo.team_b else None,
                'placar_palpite': f"{p.result_a}x{p.result_b}",
                'placar_real': f"{jogo.team_a_result}x{jogo.team_b_result}",
                'pontos': pontos,
                'tipo': tipo
            })
            
    return jsonify({
        "status": "success", 
        "nome": user.name, 
        "profile_pic": user.profile_pic,
        "historico": historico
    })

@main_bp.route('/api/evolucao_participantes')
@login_required
def api_evolucao_participantes():
    jogos_encerrados = Game.query.options(joinedload(Game.team_a), joinedload(Game.team_b)).filter_by(status='encerrado').order_by(Game.datetime_game).all()
    todos_usuarios = User.query.filter_by(is_approved=True).all()
    
    ids_jogos = [j.id for j in jogos_encerrados]
    todos_palpites = Prediction.query.filter(Prediction.game_id.in_(ids_jogos)).order_by(Prediction.created_at.desc()).all()
    
    mapa_geral = defaultdict(dict)
    for p in todos_palpites:
        if p.user_id not in mapa_geral[p.game_id]:
            mapa_geral[p.game_id][p.user_id] = p

    evolucao_all = {}
    labels_raw = [j.datetime_game.strftime('%d/%m') for j in jogos_encerrados]
    labels = []
    seen = set()
    for l in labels_raw:
        if l not in seen:
            labels.append(l)
            seen.add(l)

    for user in todos_usuarios:
        user_points = defaultdict(int)
        for jogo in jogos_encerrados:
            dia = jogo.datetime_game.strftime('%d/%m')
            p_obj = mapa_geral[jogo.id].get(user.id)
            if p_obj:
                pts, _ = calcular_pontos_palpite(p_obj.result_a, p_obj.result_b, jogo.team_a_result, jogo.team_b_result)
                user_points[dia] += pts
        
        acc = 0
        ponto_acumulado = []
        for l in labels:
            acc += user_points[l]
            ponto_acumulado.append(acc)
        
        evolucao_all[user.id] = ponto_acumulado
        
    return jsonify({
        "status": "success",
        "labels": labels,
        "usuarios": evolucao_all
    })

@main_bp.route('/perfil')
@login_required
def perfil():
    jogos_encerrados = Game.query.options(joinedload(Game.team_a), joinedload(Game.team_b)).filter_by(status='encerrado').order_by(Game.datetime_game).all()
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

    # --- NOVAS MÉTRICAS PARA TESTE ---
    ranking_users = []
    for user in todos_usuarios:
        u_pts, u_ex, u_pa, u_te = 0, 0, 0, 0
        for jogo in jogos_encerrados:
            p_obj = mapa_geral[jogo.id].get(user.id)
            if p_obj:
                pts, tipo = calcular_pontos_palpite(p_obj.result_a, p_obj.result_b, jogo.team_a_result, jogo.team_b_result)
                u_pts += pts
                if tipo == 'exato': u_ex += 1
                elif tipo == 'parcial': u_pa += 1
                elif tipo == 'tendencia': u_te += 1
        ranking_users.append({'id': user.id, 'pts': u_pts, 'ex': u_ex, 'pa': u_pa, 'te': u_te, 'n': user.name})
    
    ranking_users.sort(key=lambda x: (-x['pts'], -x['ex'], -x['pa'], -x['te'], x['n'].lower()))
    user_rank = next((i + 1 for i, u in enumerate(ranking_users) if u['id'] == current_user.id), 0)

    n_palpites_encerrados = len(historico)
    aproveitamento = (stats['total_pontos'] / (n_palpites_encerrados * 5) * 100) if n_palpites_encerrados > 0 else 0
    media_pontos = stats['total_pontos'] / n_palpites_encerrados if n_palpites_encerrados > 0 else 0
    
    titulo = "Novato"
    badge = "fa-seedling"
    if n_palpites_encerrados >= 3:
        if stats['exatos'] >= stats['parciais'] and stats['exatos'] >= stats['tendencia']: 
            titulo = "Sniper de Placares"
            badge = "fa-crosshairs"
        elif stats['parciais'] >= stats['exatos'] and stats['parciais'] >= stats['tendencia']: 
            titulo = "Analista Preciso"
            badge = "fa-chart-pie"
        else: 
            titulo = "Estrategista de Resultados"
            badge = "fa-chess"

    return render_template('perfil.html', stats=stats, num_trocas=num_trocas, 
                           num_palpites=len(palpites_finais_user), 
                           n_jogos_encerrados=len(jogos_encerrados),
                           total_jogos=Game.query.count(),
                           chart_labels=labels, user_data=user_acc, media_data=media_acc, 
                           historico=historico,
                           user_rank=user_rank, aproveitamento=round(aproveitamento, 1),
                           media_pontos=round(media_pontos, 1), titulo=titulo, badge=badge,
                           ranking_users=ranking_users)