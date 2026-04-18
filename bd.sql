-- 1. Tabela de Usuários
CREATE TABLE dim_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- 2. Tabela de Seleções/Times (IDs manuais via CSV)
CREATE TABLE dim_teams (
    id INTEGER PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    ab VARCHAR(3) NOT NULL,
    team_flag_url TEXT
);

-- 3. Tabela de Jogos (IDs manuais via CSV)
CREATE TABLE dim_games (
    id INTEGER PRIMARY KEY,
    datetime_game TIMESTAMP NOT NULL,
    phase VARCHAR(50) NOT NULL,
    team_a_result INTEGER,
    team_b_result INTEGER,
    placeholder_a VARCHAR(50),
    placeholder_b VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pendente',
    
    -- Chaves estrangeiras para os times (podem ser nulas antes do chaveamento)
    team_a_id INTEGER REFERENCES dim_teams(id),
    team_b_id INTEGER REFERENCES dim_teams(id)
);

-- 4. Tabela Fato de Palpites
CREATE TABLE fact_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES dim_users(id),
    game_id INTEGER NOT NULL REFERENCES dim_games(id),
    result_a INTEGER NOT NULL,
    result_b INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tabela de Classificação da Fase de Grupos
CREATE TABLE fact_group_standings (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(1) NOT NULL,
    team_id INTEGER NOT NULL REFERENCES dim_teams(id),
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    goal_difference INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    
    -- Garante que um time não seja duplicado dentro do mesmo grupo
    CONSTRAINT fact_group_standings_group_team_key UNIQUE (group_name, team_id)
);