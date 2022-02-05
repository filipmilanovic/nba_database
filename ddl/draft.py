from utils import sql


def create_table_draft(metadata):
    metadata.reflect()
    sql.Table('draft', metadata,
              sql.Column('draft_id', sql.VARCHAR(11), primary_key=True, nullable=False),
              sql.Column('player_id', sql.VARCHAR(9)),  # no foreign key due to drafted players who never played
              sql.Column('season', sql.SMALLINT),
              sql.Column('round_number', sql.SMALLINT),
              sql.Column('round_pick', sql.SMALLINT),
              sql.Column('overall_pick', sql.SMALLINT),
              sql.Column('team_id', sql.INT),  # no foreign key due to teams that don't exist in the DB
              sql.Column('previous_team', sql.VARCHAR(64)),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
