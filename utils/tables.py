# SETTING UP SQL CONNECTIONS
import sqlalchemy as sql


def create_table_draft(engine, metadata):
    if not engine.dialect.has_table(engine, 'draft'):
        sql.Table('draft', metadata,
                  sql.Column('draft_id', sql.VARCHAR(11), primary_key=True, nullable=False),
                  sql.Column('player_id', sql.VARCHAR(9)),
                  sql.Column('season', sql.SMALLINT),
                  sql.Column('round_number', sql.SMALLINT),
                  sql.Column('round_pick', sql.SMALLINT),
                  sql.Column('overall_pick', sql.SMALLINT),
                  sql.Column('team_id', sql.INT),
                  sql.Column('previous_team', sql.VARCHAR(64)),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_games(engine, metadata):
    if not engine.dialect.has_table(engine, 'games'):
        sql.Table('games', metadata,
                  sql.Column('game_id', sql.VARCHAR(12), primary_key=True, nullable=False),
                  sql.Column('game_time', sql.DATETIME),
                  sql.Column('arena', sql.VARCHAR(64)),
                  sql.Column('national_broadcast', sql.VARCHAR(32)),
                  sql.Column('home_team_id', sql.INT),
                  sql.Column('home_score', sql.SMALLINT),
                  sql.Column('away_team_id', sql.INT),
                  sql.Column('away_score', sql.SMALLINT),
                  sql.Column('overtime', sql.VARCHAR(3)),
                  sql.Column('season', sql.SMALLINT),
                  sql.Column('game_type', sql.SMALLINT),
                  sql.Column('series_id', sql.VARCHAR(9)),
                  sql.Column('series_game', sql.SMALLINT),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_lineups(engine, metadata):
    if not engine.dialect.has_table(engine, 'lineups'):
        sql.Table('lineups', metadata,
                  sql.Column('lineup_id', sql.VARCHAR(17), primary_key=True),
                  sql.Column('game_id', sql.VARCHAR(12), index=True, nullable=False),
                  sql.Column('team_id', sql.INT),
                  sql.Column('player_id', sql.VARCHAR(9)),
                  sql.Column('seconds', sql.SMALLINT),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_players(engine, metadata):
    if not engine.dialect.has_table(engine, 'players'):
        sql.Table('players', metadata,
                  sql.Column('player_id', sql.VARCHAR(9), primary_key=True, nullable=False),
                  sql.Column('player_name', sql.VARCHAR(64)),
                  sql.Column('height', sql.SMALLINT),
                  sql.Column('weight', sql.SMALLINT),
                  sql.Column('country', sql.VARCHAR(32)),
                  sql.Column('college', sql.VARCHAR(64)),
                  sql.Column('position', sql.VARCHAR(16)),
                  sql.Column('latest_team_id', sql.INT),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_playoffs(engine, metadata):
    if not engine.dialect.has_table(engine, 'playoffs'):
        sql.Table('playoffs', metadata,
                  sql.Column('series_id', sql.VARCHAR(9), primary_key=True, nullable=False),
                  sql.Column('conference', sql.VARCHAR(16)),
                  sql.Column('playoff_round', sql.SMALLINT),
                  sql.Column('higher_seed_team_id', sql.INT),
                  sql.Column('higher_seed', sql.SMALLINT),
                  sql.Column('lower_seed_team_id', sql.INT),
                  sql.Column('lower_seed', sql.SMALLINT),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_plays(engine, metadata):
    if not engine.dialect.has_table(engine, 'plays'):
        sql.Table('plays', metadata,
                  sql.Column('play_id', sql.VARCHAR(16), primary_key=True, nullable=False),
                  sql.Column('game_id', sql.VARCHAR(12)),
                  sql.Column('period', sql.VARCHAR(3)),
                  sql.Column('game_clock', sql.TIME),
                  sql.Column('score', sql.VARCHAR(9)),
                  sql.Column('team_id', sql.INT),
                  sql.Column('player_id', sql.VARCHAR(9)),
                  sql.Column('event_name', sql.VARCHAR(50)),
                  sql.Column('event_value', sql.SMALLINT),
                  sql.Column('event_detail', sql.VARCHAR(32)),
                  sql.Column('possession', sql.SMALLINT),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_plays_players(engine, metadata):
    if not engine.dialect.has_table(engine, 'plays_players'):
        sql.Table('plays_players', metadata,
                  sql.Column('play_id', sql.VARCHAR(16), primary_key=True, nullable=False),
                  sql.Column('game_id', sql.VARCHAR(12)),
                  sql.Column('players', sql.VARCHAR(49)),
                  sql.Column('opp_players', sql.VARCHAR(49)),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_plays_raw(engine, metadata):
    if not engine.dialect.has_table(engine, 'plays_raw'):
        sql.Table('plays_raw', metadata,
                  sql.Column('game_id', sql.VARCHAR(12)),
                  sql.Column('plays', sql.VARCHAR(128)),
                  sql.Column('player_1', sql.VARCHAR(9)),
                  sql.Column('player_2', sql.VARCHAR(9)),
                  sql.Column('player_3', sql.VARCHAR(9)),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_standings(engine, metadata):
    if not engine.dialect.has_table(engine, 'standings'):
        sql.Table('standings', metadata,
                  sql.Column('team_season_id', sql.BIGINT, primary_key=True, nullable=False),
                  sql.Column('season', sql.SMALLINT),
                  sql.Column('team_id', sql.INT),
                  sql.Column('wins', sql.SMALLINT),
                  sql.Column('losses', sql.SMALLINT),
                  sql.Column('playoff_seed', sql.SMALLINT),
                  sql.Column('league_rank', sql.SMALLINT),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_teams(engine, metadata):
    if not engine.dialect.has_table(engine, 'teams'):
        sql.Table('teams', metadata,
                  sql.Column('team_season_id', sql.BIGINT, primary_key=True, nullable=False),
                  sql.Column('team_id', sql.INT),
                  sql.Column('team_name', sql.VARCHAR(33)),
                  sql.Column('abbreviation', sql.VARCHAR(3)),
                  sql.Column('conference', sql.VARCHAR(4)),
                  sql.Column('division', sql.VARCHAR(10)),
                  sql.Column('season', sql.INT),
                  sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
        metadata.create_all()


def create_table_transactions(metadata):
    sql.Table('transactions', metadata,
              sql.Column('transaction_id', sql.VARCHAR(16), primary_key=True, nullable=False),
              sql.Column('transaction_date', sql.DATE),
              sql.Column('transaction_type', sql.VARCHAR(32)),
              sql.Column('team_id', sql.INT),
              sql.Column('player_id', sql.INT),
              sql.Column('utc_written_at', sql.DATETIME, server_default=sql.func.now()))
    metadata.create_all()
