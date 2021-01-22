# DEFINE SQL QUERY FOR GENERATING EMPTY TABLES
from modelling.projects.nba.utils.connections import *


def create_table_games():
    if not engine.dialect.has_table(engine, 'games'):
        sql.Table('games', metadata,
                  sql.Column('game_id', sql.VARCHAR(12), primary_key=True, nullable=False),
                  sql.Column('game_date', sql.DATE),
                  sql.Column('home_team', sql.VARCHAR(3)),
                  sql.Column('home_score', sql.SMALLINT),
                  sql.Column('away_team', sql.VARCHAR(3)),
                  sql.Column('away_score', sql.SMALLINT),
                  sql.Column('season', sql.SMALLINT),
                  sql.Column('is_playoffs', sql.SMALLINT))
        metadata.create_all()


def create_table_games_lineups():
    if not engine.dialect.has_table(engine, 'games_lineups'):
        sql.Table('games_lineups', metadata,
                  sql.Column('game_id', sql.VARCHAR(12), index=True, nullable=False),
                  sql.Column('team_id', sql.VARCHAR(3)),
                  sql.Column('player_id', sql.VARCHAR(9)),
                  sql.Column('role', sql.VARCHAR(7)))
        metadata.create_all()


def create_table_odds():
    if not engine.dialect.has_table(engine, 'odds'):
        sql.Table('odds', metadata,
                  sql.Column('game_id', sql.VARCHAR(12), index=True, nullable=False),
                  sql.Column('home_odds', sql.DECIMAL(4, 2)),
                  sql.Column('away_odds', sql.DECIMAL(4, 2)))
        metadata.create_all()


def create_table_players():
    if not engine.dialect.has_table(engine, 'players'):
        sql.Table('players', metadata,
                  sql.Column('player_id', sql.VARCHAR(9), primary_key=True, nullable=False),
                  sql.Column('player_name', sql.VARCHAR(64)),
                  sql.Column('dob', sql.DATE),
                  sql.Column('height', sql.SMALLINT),
                  sql.Column('weight', sql.SMALLINT),
                  sql.Column('hand', sql.VARCHAR(5)),
                  sql.Column('position', sql.VARCHAR(16)),
                  sql.Column('draft_year', sql.SMALLINT),
                  sql.Column('draft_pick', sql.SMALLINT),
                  sql.Column('rookie_year', sql.SMALLINT))
        metadata.create_all()


def create_table_plays():
    if not engine.dialect.has_table(engine, 'plays'):
        sql.Table('plays', metadata,
                  sql.Column('play_id', sql.VARCHAR(16), primary_key=True, nullable=False),
                  sql.Column('game_id', sql.VARCHAR(12)),
                  sql.Column('period', sql.VARCHAR(3)),
                  sql.Column('time', sql.TIME),
                  sql.Column('score', sql.VARCHAR(7)),
                  sql.Column('team_id', sql.VARCHAR(3)),
                  sql.Column('player_id', sql.VARCHAR(9)),
                  sql.Column('event', sql.VARCHAR(32)),
                  sql.Column('event_value', sql.SMALLINT),
                  sql.Column('event_detail', sql.VARCHAR(32)),
                  sql.Column('possession', sql.SMALLINT))
        metadata.create_all()


def create_table_plays_raw():
    if not engine_raw.dialect.has_table(engine_raw, 'plays_raw'):
        sql.Table('plays_raw', metadata_raw,
                  sql.Column('game_id', sql.VARCHAR(12)),
                  sql.Column('plays', sql.VARCHAR(128)),
                  sql.Column('player_1', sql.VARCHAR(9)),
                  sql.Column('player_2', sql.VARCHAR(9)),
                  sql.Column('player_3', sql.VARCHAR(9)))
        metadata_raw.create_all()


def create_table_teams():
    sql.Table('teams', metadata,
              sql.Column('team_id', sql.VARCHAR(3), primary_key=True, nullable=False),
              sql.Column('short_name', sql.VARCHAR(32)),
              sql.Column('full_name', sql.VARCHAR(33)),
              sql.Column('coordinates', sql.VARCHAR(32)))
    metadata.drop_all()
    metadata.create_all()
