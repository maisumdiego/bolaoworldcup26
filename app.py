from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict

# IMPORTAÇÃO DOS NOSSOS MODELOS
from models import db, User, Team, Game, Prediction, GroupStanding

load_dotenv()
app = Flask(__name__)

# CONFIGURAÇÕES GERAIS
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
email_admin = os.getenv('EMAIL_ADMIN')

# CONEXÃO COM O BANCO AO APP
db.init_app(app)

# INICIALIZA O LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

## Rota do login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =======================================
# FUNÇÕES DO APP
# =======================================

def atualizar_classificacao_grupos():
    # 1. Busca todos os times na tabela de classificação
    standings = GroupStanding.query.all()
    stats_dict = {s.team_id: s for s in standings}
    
    # 2. Zera todas as métricas (Limpeza do ETL)
    for s in standings:
        s.matches_played = s.wins = s.draws = s.losses = 0
        s.goals_for = s.goals_against = s.goal_difference = s.points = 0

    # 3. Busca apenas os jogos encerrados da Fase de Grupos
    jogos_grupos = Game.query.filter(Game.status == 'encerrado', Game.phase == 'Grupos').all()

    # 4. Aplica a matemática do futebol
    for jogo in jogos_grupos:
        r_a = jogo.team_a_result
        r_b = jogo.team_b_result
        
        # Computa para o Time A
        if jogo.team_a_id in stats_dict:
            st_a = stats_dict[jogo.team_a_id]
            st_a.matches_played += 1
            st_a.goals_for += r_a
            st_a.goals_against += r_b
            st_a.goal_difference += (r_a - r_b)
            
            if r_a > r_b:
                st_a.wins += 1
                st_a.points += 3
            elif r_a == r_b:
                st_a.draws += 1
                st_a.points += 1
            else:
                st_a.losses += 1
                
        # Computa para o Time B
        if jogo.team_b_id in stats_dict:
            st_b = stats_dict[jogo.team_b_id]
            st_b.matches_played += 1
            st_b.goals_for += r_b
            st_b.goals_against += r_a
            st_b.goal_difference += (r_b - r_a)
            
            if r_b > r_a:
                st_b.wins += 1
                st_b.points += 3
            elif r_b == r_a:
                st_b.draws += 1
                st_b.points += 1
            else:
                st_b.losses += 1

    # Salva o recálculo no banco
    db.session.commit()

def automatizar_chaveamento():
    # Pega a tabela de classificação atualizada
    standings = GroupStanding.query.all()
    
    # Agrupa por letra do grupo
    grupos = defaultdict(list)
    for s in standings:
        grupos[s.group_name].append(s)
        
    # Busca todos os jogos que NÃO são da fase de grupos
    jogos_mata_mata = Game.query.filter(Game.phase != 'Grupos').all()

    for letra, times in grupos.items():
        # Soma quantos jogos os times desse grupo já jogaram
        total_partidas_grupo = sum(t.matches_played for t in times)
        
        # Se for 12 (4 times x 3 jogos), o grupo está finalizado!
        if total_partidas_grupo == 12:
            # Ordena pela regra da FIFA
            times.sort(key=lambda x: (x.points, x.goal_difference, x.goals_for), reverse=True)
            primeiro = times[0].team_id
            segundo = times[1].team_id
            
            tag_primeiro = f"1{letra}"
            tag_segundo = f"2{letra}"
            
            for jogo in jogos_mata_mata:
                # Substitui o Time A
                if jogo.placeholder_a == tag_primeiro:
                    jogo.team_a_id = primeiro
                elif jogo.placeholder_a == tag_segundo:
                    jogo.team_a_id = segundo
                    
                # Substitui o Time B
                if jogo.placeholder_b == tag_primeiro:
                    jogo.team_b_id = primeiro
                elif jogo.placeholder_b == tag_segundo:
                    jogo.team_b_id = segundo
                    
        else:
            # Reversibilidade: Se o grupo não estiver 100% finalizado
            tag_primeiro = f"1{letra}"
            tag_segundo = f"2{letra}"
            
            for jogo in jogos_mata_mata:
                if jogo.placeholder_a in [tag_primeiro, tag_segundo]:
                    jogo.team_a_id = None
                if jogo.placeholder_b in [tag_primeiro, tag_segundo]:
                    jogo.team_b_id = None

    db.session.commit()

# =======================================
# ROTAS DO APP
# =======================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('index')) 
    else:
        return "<h1>Erro: E-mail ou senha incorretos!</h1>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/register', methods=['GET', 'POST'])
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
        new_user = User(name=name, email=email, phone=phone, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/palpites')
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

@app.route('/salvar_palpite', methods=['POST'])
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

@app.route('/admin/resultados')
@login_required
def admin_resultados():
    # Segurança extra
    if current_user.email != email_admin:
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for('index'))
    
    jogos = Game.query.order_by(Game.datetime_game).all()
    
    jogos_por_fase = {}
    for jogo in jogos:
        if jogo.phase not in jogos_por_fase:
            jogos_por_fase[jogo.phase] = []
        jogos_por_fase[jogo.phase].append(jogo)
        
    fases_ordenadas = list(jogos_por_fase.keys())
    fase_ativa = fases_ordenadas[0] if fases_ordenadas else None
    
    todos_times = Team.query.order_by(Team.name).all()
    
    jogos_pendentes = Game.query.filter(
        (Game.phase != 'Grupos') & 
        ((Game.team_a_id == None) | (Game.team_b_id == None))
    ).order_by(Game.id).all()

    return render_template('admin_resultados.html', 
                           jogos_por_fase=jogos_por_fase,
                           fases_ordenadas=fases_ordenadas,
                           fase_ativa=fase_ativa,
                           todos_times=todos_times, 
                           jogos_pendentes=jogos_pendentes)

@app.route('/admin/salvar_resultado', methods=['POST'])
@login_required
def salvar_resultado():
    if current_user.email != email_admin:
        return jsonify({"status": "error", "message": "Não autorizado"}), 403

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
   
            return jsonify({"status": "success", "message": "Resultado Gravado"})
        except ValueError:
            return jsonify({"status": "error", "message": "Valores inválidos"})
            
    return jsonify({"status": "error", "message": "Jogo não encontrado"}), 404

@app.route('/ranking')
@login_required
def ranking():
    usuarios = User.query.all()
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

@app.route('/init_grupos')
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

@app.route('/torneio')
@login_required
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

@app.route('/admin/salvar_pendente', methods=['POST'])
@login_required
def salvar_pendente():
    # Verifica se é admin (use a mesma regra que você já usa nas outras rotas)
    
    game_id = request.form.get('game_id')
    team_a_id = request.form.get('team_a_id')
    team_b_id = request.form.get('team_b_id')
    
    jogo = Game.query.get(game_id)
    if not jogo:
        return jsonify({"status": "error", "message": "Jogo não encontrado."}), 404
        
    try:
        # Se o admin selecionou um time, atualizamos o ID no banco
        if team_a_id:
            jogo.team_a_id = team_a_id
        if team_b_id:
            jogo.team_b_id = team_b_id
            
        db.session.commit()
        return jsonify({"status": "success", "message": "Confronto atualizado com sucesso!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)