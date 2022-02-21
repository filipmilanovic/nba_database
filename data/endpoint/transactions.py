def get_transactions_data():
    """ set up iterations to get all scripts """
    response = r.request(method='GET',
                         url=url,
                         headers=nba_headers).json()

    tidy_data = tidy_json(response)
    output = check_db_duplicates(tidy_data, False, 'transaction_id', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                 metadata, engine, connection)

    return output


def tidy_json(json):
    """ generate cleaned scripts for each transaction """
    output = [get_transaction_data(value) for value in json['NBA_Player_Movement']['rows']]

    return output


def get_transaction_data(transaction: dict):
    """ transform transaction to cleaned dict """
    output = {'transaction_id': get_hash(transaction['TRANSACTION_DESCRIPTION'] + transaction['GroupSort'], 16),
              'transaction_date': dt.strptime(transaction['TRANSACTION_DATE'], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d'),
              'transaction_type': transaction['Transaction_Type'],
              'team_id': int(transaction['TEAM_ID']),
              'player_id': int(transaction['PLAYER_ID'])
              }

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])
    create_table_transactions(metadata)

    TARGET_TABLE = 'transactions'
    TABLE_PRIMARY_KEY = 'transaction_id'

    url = 'https://stats.nba.com/js/data/playermovement/NBA_Player_Movement.json'

    transactions_data = get_transactions_data()

    write_data(engine, metadata, connection, transactions_data, TARGET_TABLE, TABLE_PRIMARY_KEY)

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)
