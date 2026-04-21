from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from collections import defaultdict
from models import db, Game, Prediction, User, GroupStanding, Team

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
                           dias_semana=dias_semana, # Passando o dicionário para o HTML
                           grupos_ordenados=grupos_ordenados,
                           fases_ordenadas=fases_ordenadas,
                           dia_ativo=dia_ativo,
                           grupo_ativo=grupo_ativo,
                           fase_ativa=fase_ativa,
                           agora=datetime.now(),
                           timedelta=timedelta,
                           palpites_usuario=palpites_usuario)

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

@main_bp.route('/ranking')
@login_required
def ranking():
    usuarios = User.query.filter_by(is_approved=True).all()
    jogos_encerrados = Game.query.filter_by(status='encerrado').all()
    ranking_data = []

    for user in usuarios:
        pontos_totais = acertos_exatos = acertos_parciais = acertos_tendencia = 0
        palpites_raw = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()

        palpites_finais = {p.game_id: p for p in palpites_raw}

        for jogo in jogos_encerrados:
            palpite = palpites_finais.get(jogo.id)
            if palpite:
                p_a, p_b = palpite.result_a, palpite.result_b
                r_a, r_b = jogo.team_a_result, jogo.team_b_result

                if p_a == r_a and p_b == r_b:
                    pontos_totais += 5; acertos_exatos += 1
                elif (p_a > p_b and r_a > r_b) or (p_a < p_b and r_a < r_b) or (p_a == p_b and r_a == r_b):
                    if p_a == r_a or p_b == r_b: pontos_totais += 3; acertos_parciais += 1
                    else: pontos_totais += 2; acertos_tendencia += 1
        
        ranking_data.append({
            'nome': user.name, 'pontos': pontos_totais, 'exatos': acertos_exatos,
            'parciais': acertos_parciais, 'tendencia': acertos_tendencia
        })
    
    ranking_data.sort(key=lambda x: (x['pontos'], x['exatos'], x['parciais'], x['tendencia']), reverse=True)
    return render_template('ranking.html', ranking=ranking_data)

@main_bp.route('/init_grupos')
def init_grupos():
    if GroupStanding.query.first(): return "Grupos já inicializados."
    times = Team.query.all()
    letras_grupos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    
    for i, time in enumerate(times):
        indice = (i // 4) % len(letras_grupos)
        novo_time = GroupStanding(group_name=letras_grupos[indice], team_id=time.id)
        db.session.add(novo_time)

    db.session.commit()
    return "✅ SUCESSO!"

@main_bp.route('/torneio')
def torneio():
    standings = GroupStanding.query.all()
    grupos_dict = defaultdict(list)
    for s in standings: grupos_dict[s.group_name].append(s)
    for g in grupos_dict: grupos_dict[g].sort(key=lambda x: (x.points, x.goal_difference, x.goals_for), reverse=True)
    grupos_ordenados = dict(sorted(grupos_dict.items()))

    jogos_mata_mata = Game.query.filter(Game.phase != 'Grupos').order_by(Game.id).all()
    
    jogos_json = [{
        'id': j.id, 'phase': j.phase,
        'team_a_name': j.team_a.ab if j.team_a else j.placeholder_a,
        'team_b_name': j.team_b.ab if j.team_b else j.placeholder_b,
        'team_a_flag': j.team_a.team_flag_url if j.team_a else None,
        'team_b_flag': j.team_b.team_flag_url if j.team_b else None,
        'score_a': j.team_a_result if j.status == 'encerrado' else None,
        'score_b': j.team_b_result if j.status == 'encerrado' else None
    } for j in jogos_mata_mata]
        
    return render_template('torneio.html', grupos=grupos_ordenados, jogos_mata_mata=jogos_json)

@main_bp.route('/get_palpites_jogo/<int:jogo_id>')
@login_required
def get_palpites_jogo(jogo_id):
    jogo = Game.query.get_or_404(jogo_id)
    agora = datetime.now()
    visibilidade_liberada = (jogo.status == 'encerrado') or (agora >= (jogo.datetime_game - timedelta(minutes=10)))
    palpites_all = Prediction.query.filter_by(game_id=jogo_id).order_by(Prediction.created_at.desc()).all()
    
    ultimos_palpites = {}
    r_a, r_b = jogo.team_a_result, jogo.team_b_result

    for p in palpites_all:
        if p.user_id not in ultimos_palpites:
            user = User.query.get(p.user_id)
            nome_usuario = user.name if user else "Anônimo"
            
            if visibilidade_liberada:
                pontos = 0
                if jogo.status == 'encerrado':
                    if p.result_a == r_a and p.result_b == r_b: pontos = 5
                    elif (p.result_a > p.result_b and r_a > r_b) or (p.result_a < p.result_b and r_a < r_b) or (p.result_a == p.result_b and r_a == r_b):
                        pontos = 3 if (p.result_a == r_a or p.result_b == r_b) else 2
                ultimos_palpites[p.user_id] = {"nome": nome_usuario, "result_a": p.result_a, "result_b": p.result_b, "pontos": pontos, "liberado": True}
            else:
                ultimos_palpites[p.user_id] = {"nome": nome_usuario, "liberado": False}
        
    return jsonify({"status": "success", "visibilidade_liberada": visibilidade_liberada, "palpites": list(ultimos_palpites.values())})