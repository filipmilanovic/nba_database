from utils import sql


def create_table_plays(metadata):
    metadata.reflect()
    sql.Table('plays', metadata,
              sql.Column('play_id', sql.VARCHAR(16), primary_key=True, nullable=False),
              sql.Column('game_id', sql.VARCHAR(12), sql.ForeignKey('games.game_id')),
              sql.Column('period', sql.VARCHAR(3)),
              sql.Column('game_clock', sql.TIME),
              sql.Column('score', sql.VARCHAR(9)),
              sql.Column('team_id', sql.INT),  # no foreign key due to existing bugs
              sql.Column('player_id', sql.VARCHAR(9), sql.ForeignKey('players.player_id')),
              sql.Column('event_name', sql.VARCHAR(50)),
              sql.Column('event_value', sql.SMALLINT),
              sql.Column('event_detail', sql.VARCHAR(32)),
              sql.Column('possession', sql.SMALLINT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
