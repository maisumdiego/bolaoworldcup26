import pandas as pd
from app import app
from models import db, Team, Game
from datetime import datetime
from sqlalchemy import text

def ingestao_times(src):
    with app.app_context():
        try:
            df_times = pd.read_csv(src)
            for index, row in df_times.iterrows():
                # Verifica se o time já existe pela sigla ou nome
                time_existente = Team.query.filter_by(ab=row['ab']).first()
                
                if time_existente:
                    time = time_existente
                else:
                    time = Team()
                
                time.team_name = row['team_name']
                time.ab = row['ab']
                time.continent = row['continent']
                time.group_team = row['group_team']
                time.team_flag_url = row['team_flag_url']
                time.fifa_ranking = int(row['fifa_ranking']) if pd.notna(row['fifa_ranking']) else None
                time.world_cups_won = int(row['world_cups_won']) if pd.notna(row['world_cups_won']) else 0
                
                if not time_existente:
                    db.session.add(time)
            
            db.session.commit()
            print(f"Sucesso: {len(df_times)} seleções processadas.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro nos times: {e}")

ingestao_times(r"seed\Tabelas Copa 2026 - teams.csv")

def ingestao_jogos(src):
    with app.app_context():
        try:
            df_jogos = pd.read_csv(src)
            times_db = Team.query.all()
            sigla_para_id = {time.ab: time.id for time in times_db if time.ab}

            for index, row in df_jogos.iterrows():
                
                valor_a = str(row['team_a_id']) if pd.notna(row['team_a_id']) else None
                valor_b = str(row['team_b_id']) if pd.notna(row['team_b_id']) else None

                id_a = sigla_para_id.get(valor_a)
                id_b = sigla_para_id.get(valor_b)

                ph_a = str(row['placeholder_a']) if 'placeholder_a' in row and pd.notna(row['placeholder_a']) else None
                ph_b = str(row['placeholder_b']) if 'placeholder_b' in row and pd.notna(row['placeholder_b']) else None

                jogo = Game(
                    id=int(row['id']),
                    team_a_id=id_a,
                    team_b_id=id_b,
                    datetime_game=pd.to_datetime(row['datetime_game']),
                    phase=str(row['phase']),
                    placeholder_a=ph_a,
                    placeholder_b=ph_b,
                    status='agendado'
                )
                
                db.session.merge(jogo)

            db.session.commit()
            print(f"Sucesso: {len(df_jogos)} jogos processados.")

        except Exception as e:
            db.session.rollback()
            print(f"Erro: {e}")

ingestao_jogos(r"seed\Tabelas Copa 2026 - games.csv")

def consultar_tabela(query_sql, index_col):
    with app.app_context():
        with db.engine.connect() as conexao:
            df = pd.read_sql_query(query_sql, con=conexao, index_col=index_col)
        return df

with app.app_context():
    print("1. Sincronizando as Seleções...")
    df_times = pd.read_csv(r"seed\Tabelas Copa 2026 - teams.csv")
    
    # Busca os times já existentes ordenados pelo ID para bater com a linha exata do CSV
    times_db = Team.query.order_by(Team.id).all()
    
    for i, row in df_times.iterrows():
        if i < len(times_db):
            times_db[i].team_name = row['team_name']
            times_db[i].ab = row['ab']
            times_db[i].team_flag_url = row['team_flag_url']
            times_db[i].continent = row['continent']
            times_db[i].fifa_ranking = int(row['fifa_ranking']) if pd.notna(row['fifa_ranking']) else None
            times_db[i].world_cups_won = int(row['world_cups_won']) if pd.notna(row['world_cups_won']) else 0

    db.session.commit()
    print("✅ Seleções atualizadas com sucesso!")

    print("2. Sincronizando os Jogos...")
    df_jogos = pd.read_csv(r"seed\Tabelas Copa 2026 - games.csv")
    
    # Cria um dicionário com as novas siglas do banco para achar os IDs corretos
    sigla_para_id = {t.ab: t.id for t in Team.query.all() if t.ab}
    
    for index, row in df_jogos.iterrows():
        jogo = Game.query.get(int(row['id']))
        if jogo:
            valor_a = str(row['team_a_id']) if pd.notna(row['team_a_id']) else None
            valor_b = str(row['team_b_id']) if pd.notna(row['team_b_id']) else None
            
            # Só atualiza se a sigla existir no novo mapeamento
            if valor_a in sigla_para_id:
                jogo.team_a_id = sigla_para_id[valor_a]
            if valor_b in sigla_para_id:
                jogo.team_b_id = sigla_para_id[valor_b]

    db.session.commit()
    print("✅ Jogos atualizados com sucesso!")