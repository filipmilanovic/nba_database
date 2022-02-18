from utils import sql


def create_table_transactions(metadata):
    metadata.reflect()
    sql.Table('transactions', metadata,
              sql.Column('transaction_id', sql.VARCHAR(16), primary_key=True, nullable=False),
              sql.Column('transaction_date', sql.DATE),
              sql.Column('transaction_type', sql.VARCHAR(32)),
              sql.Column('team_id', sql.INT, sql.ForeignKey('teams.team_id')),
              sql.Column('player_id', sql.INT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()),
              extend_existing=True)
    metadata.create_all()
