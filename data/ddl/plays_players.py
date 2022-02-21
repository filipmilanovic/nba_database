from data.utils import sql


def create_table_plays_players(metadata):
    metadata.reflect()
    sql.Table('plays_players', metadata,
              sql.Column('play_id', sql.VARCHAR(16), primary_key=True, nullable=False),
              sql.Column('game_id', sql.VARCHAR(12)),
              sql.Column('players', sql.VARCHAR(49)),
              sql.Column('opp_players', sql.VARCHAR(49)),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
