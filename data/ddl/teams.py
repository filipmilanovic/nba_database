import sqlalchemy as sql


def create_table_teams(metadata):
    sql.Table('teams', metadata,
              sql.Column('team_season_id', sql.BIGINT, primary_key=True, nullable=False),
              sql.Column('team_id', sql.INT, index=True),
              sql.Column('team_name', sql.VARCHAR(33)),
              sql.Column('abbreviation', sql.VARCHAR(3)),
              sql.Column('conference', sql.VARCHAR(4)),
              sql.Column('division', sql.VARCHAR(10)),
              sql.Column('season', sql.INT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
    metadata.create_all()

