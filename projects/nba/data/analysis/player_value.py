# FIND VALUE OF EACH PLAYER
from modelling.projects.nba.utils import *  # import user defined utilities


def get_plays_indices():
    """ get the plays the given players was involved in """
    player_plays_boolean = [player_id in play for play in players_list]
    opp_player_plays_boolean = [player_id in play for play in opp_players_list]

    index_1 = [i for i, x in enumerate(player_plays_boolean) if x]
    index_2 = [i for i, x in enumerate(opp_player_plays_boolean) if x]

    return index_1, index_2


def get_score_list(index):
    """ get the list of scoring events for the given index """
    output = [event_value_list[i] if event_list[i] in ['FG Make', 'FT Make'] else 0 for i in index]

    return output


def get_team_scores(current_player_id, player_list, index):
    """ input the latest player scores for each team for possession for the given index """
    output = [sum([latest_iteration[player]['value'] for player in player_list[i].split('|')
                   if player != current_player_id])
              for i in index]

    return output


def get_player_score(list_1, list_2, list_3):
    """ calculate the score for the current player """
    output = sum([x - y + z for x, y, z in zip(list_1, list_2, list_3)])

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)
    engine_analysis, metadata_analysis, connection_analysis = get_connection(database_analysis)

    df_sql = sql.Table('season_plays', metadata_analysis, autoload=True, autoload_with=engine_analysis)
    season_plays = pd.read_sql(sql=sql.select([df_sql]), con=engine_analysis)

    query = get_join_query(metadata, engine, 'games', 'games_lineups', 'season', [2020])

    season_players = pd.read_sql(sql=query, con=engine)
    player_ids = season_players['player_id'].unique()

    latest_iteration = {player: {'value': 0} for player in player_ids}
    latest_deltas = []
    max_delta = 1

    while max_delta > 0.001:
        # set dictionary for latest iteration
        current_iteration = {}
        current_deltas = []

        # get index of all possessions and scoring plays
        possession_index = (season_plays['possession'] == 1) | (season_plays['event'] == 'FT Make')

        # convert all series' to lists
        players_list = season_plays.loc[possession_index, 'players'].tolist()
        opp_players_list = season_plays.loc[possession_index, 'opp_players'].tolist()
        event_list = season_plays.loc[possession_index, 'event'].tolist()
        event_value_list = season_plays.loc[possession_index, 'event_value'].tolist()
        possession_list = season_plays.loc[possession_index, 'possession'].tolist()

        for iteration in range(len(player_ids)):
            start_time = time.time()

            player_id = player_ids[iteration]

            # get player indices
            player_index, opp_player_index = get_plays_indices()

            # get list of scoring events
            score_list = get_score_list(player_index)
            opp_score_list = get_score_list(opp_player_index)

            # get player scores for team and opponent when team scores
            team_score = get_team_scores(player_id, players_list, player_index)
            team_score_opp = get_team_scores(player_id, opp_players_list, player_index)

            # get player scores for team and opponent when opponent scores
            opp_score = get_team_scores(player_id, opp_players_list, opp_player_index)
            opp_score_opp = get_team_scores(player_id, players_list, opp_player_index)

            # calculate player and opponent scores
            player_score = get_player_score(score_list, team_score, team_score_opp)
            player_opp_score = get_player_score(opp_score_list, opp_score, opp_score_opp)

            # find number of possessions player was on for and calculate average player possession value
            player_possessions = sum([possession_list[i] for i in player_index + opp_player_index])

            try:
                player_possession_value = round((player_score - player_opp_score) / player_possessions, 5)
            except ZeroDivisionError:
                player_possession_value = player_score - player_opp_score

            # store value in current dict
            # WOULD BE GOOD TO ADD OFFENSIVE/DEFENSIVE VALUE
            current_iteration[player_id] = {'value': player_possession_value, 'possessions': player_possessions}

            # find delta from previous iteration and store in list
            d = abs(player_possession_value - latest_iteration[player_id]['value'])
            current_deltas.append(d)

            calculation_time = time.time() - start_time

            time_taken = "{:.2f}".format(calculation_time) + ' seconds Total ' + time_lapsed()

            progress(iteration=iteration,
                     iterations=len(player_ids),
                     iteration_name=player_id + f' {player_possession_value}',
                     lapsed=time_taken)

        max_delta = max(current_deltas)
        print(f'end of current iteration, max delta = {max_delta}')
        latest_iteration = current_iteration

    player_value = pd.DataFrame.from_dict(data=latest_iteration,
                                          orient='index',
                                          columns=['value', 'possessions'])

    player_value['player_id'] = player_value.index
    player_value = player_value.reset_index(drop=True)

    status = write_data(df=player_value,
                        name='player_value',
                        sql_engine=engine_analysis,
                        db_schema='nba_analysis',
                        if_exists='append',
                        index=False)

    print(f"Finished and {status['sql']}")
