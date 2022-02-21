from data.utils import sql


def create_table_playoffs(metadata):
    metadata.reflect()
    sql.Table('playoffs', metadata,
              sql.Column('series_id', sql.VARCHAR(9), primary_key=True),  # no foreign key due to missing scripts
              sql.Column('conference', sql.VARCHAR(16)),
              sql.Column('playoff_round', sql.SMALLINT),
              sql.Column('higher_seed_team_id', sql.INT,  sql.ForeignKey('teams.team_id')),
              sql.Column('higher_seed', sql.SMALLINT),
              sql.Column('lower_seed_team_id', sql.INT, sql.ForeignKey('teams.team_id')),
              sql.Column('lower_seed', sql.SMALLINT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
