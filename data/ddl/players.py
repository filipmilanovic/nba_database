from data.utils import sql


def create_table_players(metadata):
    metadata.reflect()
    sql.Table('players', metadata,
              sql.Column('player_id', sql.VARCHAR(9), primary_key=True),
              sql.Column('player_name', sql.VARCHAR(64)),
              sql.Column('height', sql.SMALLINT),
              sql.Column('weight', sql.SMALLINT),
              sql.Column('country', sql.VARCHAR(32)),
              sql.Column('college', sql.VARCHAR(64)),
              sql.Column('position', sql.VARCHAR(16)),
              sql.Column('latest_team_id', sql.INT),  # no foreign key due to potential for outdated teams
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
