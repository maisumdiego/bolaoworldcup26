from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# INICIALIZA O SQLALCHEMY
db = SQLAlchemy()

# =========================================
# TABELAS MODELOS NO PYTHON PARA SQLALCHEMY
# =========================================

class User(UserMixin, db.Model):
    __tablename__ = 'dim_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(120), nullable=False, default='default.png')

class Team(db.Model):
    __tablename__ = 'dim_teams'
    
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(50), nullable=False)
    ab = db.Column(db.String(3))
    continent = db.Column(db.String(50))
    group_team = db.Column(db.String(1))
    team_flag_url = db.Column(db.String(100))
    fifa_ranking = db.Column(db.Integer)
    world_cups_won = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

class Game(db.Model):
    __tablename__ = 'dim_games'
    id = db.Column(db.Integer, primary_key=True)
    team_a_id = db.Column(db.Integer, db.ForeignKey('dim_teams.id')) 
    team_a_result = db.Column(db.Integer)
    team_b_id = db.Column(db.Integer, db.ForeignKey('dim_teams.id'))
    team_b_result = db.Column(db.Integer)
    datetime_game = db.Column(db.DateTime, nullable=False)
    phase = db.Column(db.String(50))
    status = db.Column(db.String(15), default='agendado')
    placeholder_a = db.Column(db.String(50))
    placeholder_b = db.Column(db.String(50))
    penalties_winner_id = db.Column(db.Integer, db.ForeignKey('dim_teams.id'), nullable=True)
    team_a = db.relationship('Team', foreign_keys=[team_a_id])
    team_b = db.relationship('Team', foreign_keys=[team_b_id])

class Prediction(db.Model):
    __tablename__ = 'fact_predictions'
    id = db.Column(db.Integer, primary_key=True)
    # As chaves estrangeiras apontando para o usuário e para o jogo
    user_id = db.Column(db.Integer, db.ForeignKey('dim_users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('dim_games.id'), nullable=False)
    result_a = db.Column(db.Integer, nullable=False)
    result_b = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupStanding(db.Model):
    __tablename__ = 'fact_group_standings'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('dim_teams.id'), nullable=False)
    group_name = db.Column(db.String(1), nullable=False)
    
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    goal_difference = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    # Permite você fazer: classificacao.team.team_name e pegar "Brasil" direto
    team = db.relationship('Team', backref='standings')

class Config(db.Model):
    __tablename__ = 'dim_configs'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)