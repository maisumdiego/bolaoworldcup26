from app import app
from models import db, Team, GroupStanding

def popular_classificacao():
    with app.app_context():
        try:
            # Busca todos os times
            times = Team.query.all()
            if not times:
                print("Nenhum time encontrado no banco para popular a classificação.")
                return

            # Limpa classificação atual para evitar duplicatas
            GroupStanding.query.delete()
            
            # Cria entrada para cada time
            for time in times:
                if time.group_team: # Só times que pertencem a grupos
                    standing = GroupStanding(
                        team_id=time.id,
                        group_name=time.group_team,
                        matches_played=0,
                        wins=0,
                        draws=0,
                        losses=0,
                        goals_for=0,
                        goals_against=0,
                        goal_difference=0,
                        points=0
                    )
                    db.session.add(standing)
            
            db.session.commit()
            print(f"Sucesso: Classificação inicial de {len(times)} seleções criada.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao popular classificação: {e}")

if __name__ == "__main__":
    popular_classificacao()
