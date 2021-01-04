# DEFINE SQL QUERY FOR GENERATING EMPTY TABLES
from modelling.projects.nba.utils.connections import *


def create_table_games():
    if not engine.dialect.has_table(engine, 'games'):
        sql.Table('games', metadata,
                  Column('game_id', VARCHAR(12), primary_key=True, nullable=False),
                  Column('date', DATE),
                  Column('home_team', VARCHAR(3)),
                  Column('home_score', SMALLINT),
                  Column('away_team', VARCHAR(3)),
                  Column('away_score', SMALLINT),
                  Column('season', SMALLINT))
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
