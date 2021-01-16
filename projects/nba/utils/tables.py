# DEFINE SQL QUERY FOR GENERATING EMPTY TABLES
from modelling.projects.nba.utils.connections import *


def create_table_games():
    if not engine.dialect.has_table(engine, 'games'):
        sql.Table('games', metadata,
                  Column('game_id', VARCHAR(12), primary_key=True, nullable=False),
                  Column('game_date', DATE),
                  Column('home_team', VARCHAR(3)),
                  Column('home_score', SMALLINT),
                  Column('away_team', VARCHAR(3)),
                  Column('away_score', SMALLINT),
                  Column('season', SMALLINT),
                  Column('is_playoffs', SMALLINT))
        metadata.create_all()


def create_table_games_lineups():
    if not engine.dialect.has_table(engine, 'games_lineups'):
        sql.Table('games_lineups', metadata,
                  Column('game_id', VARCHAR(12), index=True, nullable=False),
                  Column('team_id', VARCHAR(3)),
                  Column('player_id', VARCHAR(9)),
                  Column('role', VARCHAR(7)))
        metadata.create_all()


def create_table_odds():
    if not engine.dialect.has_table(engine, 'odds'):
        sql.Table('odds', metadata,
                  Column('game_id', VARCHAR(12), index=True, nullable=False),
                  Column('home_odds', DECIMAL(4, 2)),
                  Column('away_odds', DECIMAL(4, 2)))
        metadata.create_all()


def create_table_players():
    if not engine.dialect.has_table(engine, 'players'):
        sql.Table('players', metadata,
                  Column('player_id', VARCHAR(9), primary_key=True, nullable=False),
                  Column('player_name', VARCHAR(64)),
                  Column('dob', DATE),
                  Column('height', SMALLINT),
                  Column('weight', SMALLINT),
                  Column('hand', VARCHAR(5)),
                  Column('position', VARCHAR(16)),
                  Column('draft_year', SMALLINT),
                  Column('draft_pick', SMALLINT),
                  Column('rookie_year', SMALLINT))
        metadata.create_all()


def create_table_plays():
    if not engine.dialect.has_table(engine, 'plays'):
        sql.Table('plays', metadata,
                  Column('play_id', VARCHAR(16), primary_key=True, nullable=False),
                  Column('game_id', VARCHAR(12)),
                  Column('period', VARCHAR(3)),
                  Column('time', TIME),
                  Column('score', VARCHAR(7)),
                  Column('team_id', VARCHAR(3)),
                  Column('player_id', VARCHAR(9)),
                  Column('event', VARCHAR(32)),
                  Column('event_value', SMALLINT),
                  Column('event_detail', VARCHAR(32)),
                  Column('possession', SMALLINT))
        metadata.create_all()


def create_table_teams():
    sql.Table('teams', metadata,
              Column('team_id', VARCHAR(3), primary_key=True, nullable=False),
              Column('short_name', VARCHAR(32)),
              Column('full_name', VARCHAR(33)),
              Column('coordinates', VARCHAR(32)))
    metadata.drop_all()
    metadata.create_all()
