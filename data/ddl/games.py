from data.utils import sql


def create_table_games(metadata):
    metadata.reflect()
    sql.Table('games', metadata,
              sql.Column('game_id', sql.VARCHAR(12), primary_key=True),
              sql.Column('game_time', sql.DATETIME),
              sql.Column('arena', sql.VARCHAR(64)),
              sql.Column('national_broadcast', sql.VARCHAR(32)),
              sql.Column('home_team_id', sql.INT, sql.ForeignKey('teams.team_id')),
              sql.Column('home_score', sql.SMALLINT),
              sql.Column('away_team_id', sql.INT, sql.ForeignKey('teams.team_id')),
              sql.Column('away_score', sql.SMALLINT),
              sql.Column('overtime', sql.VARCHAR(3)),
              sql.Column('season', sql.SMALLINT),
              sql.Column('game_type', sql.SMALLINT),
              sql.Column('series_id', sql.VARCHAR(9), index=True),
              sql.Column('series_game', sql.SMALLINT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
