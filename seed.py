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
                # O merge localiza pelo ID ou cria um novo objeto
                time = Team(
                    id=int(row['id']) if 'id' in row else None,
                    team_name=row['team_name'],
                    ab=row['ab'],
                    continent=row['continent'],
                    group_team=row['group_team'],
                    team_flag_url=row['team_flag_url'],
                    fifa_ranking=int(row['fifa_ranking']) if pd.notna(row['fifa_ranking']) else None,
                    world_cups_won=int(row['worlds_cups_won']) if pd.notna(row['worlds_cups_won']) else 0
                )
                db.session.merge(time)
            
            db.session.commit()
            print(f"Sucesso: {len(df_times)} seleções processados.")
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
