from collections import defaultdict
from models import db, Game, GroupStanding

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

def avancar_mata_mata(jogo_atual):
    vencedor_id = None
    
    if jogo_atual.team_a_result > jogo_atual.team_b_result:
        vencedor_id = jogo_atual.team_a_id
    elif jogo_atual.team_b_result > jogo_atual.team_a_result:
        vencedor_id = jogo_atual.team_b_id
    else:
        print(f"🛑 Empate no jogo {jogo_atual.id}! Ninguém avança automático.")
        return 

    if not vencedor_id:
        return

    # O formato que criamos. Ex: 'W73'
    proximo_placeholder = f"W{jogo_atual.id}"
    
    print(f"🔎 DEBUG: O jogo atual é o ID {jogo_atual.id}.")
    print(f"🔎 DEBUG: Procurando o próximo jogo que tenha o placeholder exato: '{proximo_placeholder}'")

    proximo_jogo = Game.query.filter(
        (Game.placeholder_a == proximo_placeholder) | 
        (Game.placeholder_b == proximo_placeholder)
    ).first()

    if proximo_jogo:
        print(f"✅ DEBUG: Achei o próximo jogo! É o ID {proximo_jogo.id}. Injetando o time {vencedor_id}.")
        if proximo_jogo.placeholder_a == proximo_placeholder:
            proximo_jogo.team_a_id = vencedor_id
        else:
            proximo_jogo.team_b_id = vencedor_id
        db.session.commit()
    else:
        print(f"❌ DEBUG: Não achei NENHUM jogo com o texto '{proximo_placeholder}'.")