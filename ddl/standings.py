from utils import sql


def create_table_standings(metadata):
    metadata.reflect()
    sql.Table('standings', metadata,
              sql.Column('team_season_id', sql.BIGINT, sql.ForeignKey('teams.team_season_id'), primary_key=True),
              sql.Column('season', sql.SMALLINT),
              sql.Column('team_id', sql.INT, sql.ForeignKey('teams.team_id')),
              sql.Column('wins', sql.SMALLINT),
              sql.Column('losses', sql.SMALLINT),
              sql.Column('playoff_seed', sql.SMALLINT),
              sql.Column('league_rank', sql.SMALLINT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
