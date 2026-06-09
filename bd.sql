-- 1. Tabela de Usuários (dim_users)
CREATE TABLE dim_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN DEFAULT FALSE,
    profile_pic VARCHAR(120) DEFAULT 'default.png'
);

-- 2. Tabela de Seleções/Times (dim_teams)
CREATE TABLE dim_teams (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    ab VARCHAR(3) NOT NULL,
    continent VARCHAR(50),
    group_team VARCHAR(1),
    team_flag_url VARCHAR(255),
    fifa_ranking INTEGER,
    world_cups_won INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. Tabela de Jogos (dim_games)
CREATE TABLE dim_games (
    id SERIAL PRIMARY KEY,
    team_a_id INTEGER REFERENCES dim_teams(id),
    team_a_result INTEGER,
    team_b_id INTEGER REFERENCES dim_teams(id),
    team_b_result INTEGER,
    datetime_game TIMESTAMP NOT NULL,
    phase VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'agendado',
    placeholder_a VARCHAR(50), 
    placeholder_b VARCHAR(50) 
);

-- 4. Tabela de Classificação da Fase de Grupos (fact_group_standings)
CREATE TABLE fact_group_standings (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES dim_teams(id) NOT NULL,
    group_name VARCHAR(1) NOT NULL,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    goal_difference INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0
);

-- 5. Tabela de Palpites dos Usuários (fact_predictions)
CREATE TABLE fact_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES dim_users(id) NOT NULL,
    game_id INTEGER REFERENCES dim_games(id) NOT NULL,
    result_a INTEGER NOT NULL,
    result_b INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 6. Tabela de Configurações (dim_configs)
    CREATE TABLE dim_configs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );