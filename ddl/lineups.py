from utils import sql


def create_table_lineups(metadata):
    metadata.reflect()
    sql.Table('lineups', metadata,
              sql.Column('lineup_id', sql.VARCHAR(17), primary_key=True),
              sql.Column('game_id', sql.VARCHAR(12), sql.ForeignKey('games.game_id'), index=True, nullable=False),
              sql.Column('team_id', sql.INT),
              sql.Column('player_id', sql.VARCHAR(9), sql.ForeignKey('players.player_id')),
              sql.Column('seconds', sql.SMALLINT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
