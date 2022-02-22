# SETTING UP SQL CONNECTIONS
import pandas as pd


def write_row(conn, target_table: str, data: list):
    """ use this where data needs to be inserted by single row (e.g. different columns per row) """
    query = ''
    for i in range(len(data)):
        query = f"""insert into {target_table} ({", ".join(data[0].keys())}) values ('{"', '".join(data[i].values())}')"""
        conn.cursor().execute(query)
        conn.cursor().close()
        conn.commit()

    return query


def write_batch(conn, target_table: str, data: list):
    """ use this were data can be inserted by batch (e.g. known column per row) """
    values = ', '.join(["', '".join(data[i].values()) for i in range(len(data))])
    query = f"""insert into {target_table} ({", ".join(data[0].keys())}) values ('{values}')"""
    conn.cursor().execute(query)
    conn.cursor().close()
    conn.commit()

    return query


def write_data(conn, target_table: str, primary_key: str, data: list, by: str, rebuild=False):
    """ write data to the DB """
    primary_ids = [row[primary_key] for row in data]
    if not rebuild:
        delete_query = f"""delete from {target_table} where {primary_key} in ({', '.join(primary_ids)})"""
        conn.cursor().execute(delete_query)
        conn.cursor().close()
        conn.commit()

    insert_query = ''
    if by == 'row':
        insert_query = write_row(conn, target_table, data)
    elif by == 'batch':
        insert_query = write_batch(conn, target_table, data)

    return insert_query


def check_db_duplicates(conn,
                        target_table: str,
                        target_key: str,
                        data_key: str,
                        data,
                        use_headers: bool,
                        rebuild=False):
    """ check for existing observations in the DB """
    if not rebuild:
        # find rows where data already exists in DB
        skip = conn.cursor().execute(f'select {target_key} from {target_table}').fetch()
        conn.cursor().close()
        if use_headers:
            # get location for key in each row of data
            headers = data['headers']
            rows = data['rowSet']
            header_loc = headers.index(data_key)

            data['rowSet'] = [row for row in rows if str(row[header_loc]) not in skip]
        else:
            # data frame conversion helps with speed for larger checks
            data_frame = pd.DataFrame(data)

            # ensures null values all as None, as MySQL can't take nan
            check_keys = data_frame.where(pd.notnull(data_frame), None)
            data = check_keys[~check_keys[data_key].isin(skip)].to_dict(orient='records')

    output = data

    return output


def create_table(conn, target_table: str, rebuild=False):
    if rebuild:
        create_statement = open(f'ddl/{target_table}.sql', 'r').read()
        conn.cursor().execute(create_statement)
        conn.cursor().close()
        conn.commit()
