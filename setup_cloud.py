import os
import pandas as pd
from app import app
from models import db
from sqlalchemy import text, inspect

def run_setup():
    with app.app_context():
        print("Iniciando Pipeline de Dados no Railway...")

        # --- ETAPA 1: ESTRUTURA E MIGRAÇÃO ---
        try:
            inspector = inspect(db.engine)
            tabelas_existentes = inspector.get_table_names()
            
            # 1. Checa se as tabelas existem
            if 'dim_teams' not in tabelas_existentes:
                print("1/4 - Criando estrutura inicial do banco...")
                with open('bd.sql', 'r', encoding='utf-8') as file:
                    sql_script = file.read()
                db.session.execute(text(sql_script))
                db.session.commit()
            
            # 2. Checa se a coluna da migração existe
            colunas = [c['name'] for c in inspector.get_columns('dim_teams')]
            if 'worlds_cups_won' not in colunas:
                print("2/4 - Migração: Adicionando coluna 'worlds_cups_won'...")
                db.session.execute(text("ALTER TABLE dim_teams ADD COLUMN worlds_cups_won INTEGER DEFAULT 0;"))
                db.session.commit()
            else:
                print("Passo 1/2: Estrutura e colunas OK. Pulando criação.")

        except Exception as e:
            db.session.rollback()
            print(f"Erro na etapa de estrutura/migração: {e}")
            return

        # --- ETAPA 2: CARGA DE DADOS (SEED) ---
        try:
            # 3. Checa as Seleções
            print("3/4 - Verificando dados das Seleções (dim_teams)...")
            qtd_teams = db.session.execute(text("SELECT COUNT(*) FROM dim_teams")).scalar()
            
            if qtd_teams > 0:
                print(f"A tabela já possui {qtd_teams} seleções. Pulando injeção (Evitando duplicidade).")
            else:
                path_teams = os.path.join("seed", "Tabelas Copa 2026 - teams.csv")
                df_teams = pd.read_csv(path_teams)
                df_teams.to_sql('dim_teams', con=db.engine, if_exists='append', index=False)
                print(f"{len(df_teams)} seleções inseridas.")

            # 4. Checa e insere os Jogos (Com o De-Para de IDs)
            print("4/4 - Verificando dados dos Jogos (dim_games)...")
            qtd_games = db.session.execute(text("SELECT COUNT(*) FROM dim_games")).scalar()
            
            if qtd_games > 0:
                print(f"A tabela já possui {qtd_games} jogos. Pulando injeção.")
            else:
                path_games = os.path.join("seed", "Tabelas Copa 2026 - games.csv")
                df_games = pd.read_csv(path_games)
                
                print("Traduzindo siglas para IDs Numéricos...")
                # Lê o banco para saber quais IDs o Railway gerou para cada sigla
                df_teams_db = pd.read_sql("SELECT id, ab FROM dim_teams", con=db.engine)
                mapa_times = dict(zip(df_teams_db['ab'], df_teams_db['id']))
                
                # Aplica a tradução
                df_games['team_a_id'] = df_games['team_a_id'].map(mapa_times).astype('Int64')
                df_games['team_b_id'] = df_games['team_b_id'].map(mapa_times).astype('Int64')
                
                # Injeta os dados
                df_games.to_sql('dim_games', con=db.engine, if_exists='append', index=False)
                print(f"{len(df_games)} jogos inseridos com sucesso!")

            print("\n✨ PROCESSO CONCLUÍDO! Banco atualizado e populado.")

        except Exception as e:
            db.session.rollback()
            print(f"Erro na carga de dados: {e}")

if __name__ == "__main__":
    run_setup()