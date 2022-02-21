
import datetime as dt
import os
import sys
sys.path.append('.')

from airflow import DAG
from airflow.operators.python import PythonOperator
from endpoint.teams import run_teams
from utils.connections import get_connection

target_table = 'teams'
primary_key = 'team_season_id'

engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])

db = {'engine': engine,
      'metadata': metadata,
      'connection': connection}

kwargs = {'target_table': target_table,
          'primary_key': primary_key,
          'db': db}

default_args = {
    'owner': 'airflow'
}

dag = DAG('teams',
          default_args=default_args,
          description='A DAG scraping the latest teams scripts',
          schedule_interval='0 0 * * *',
          start_date=dt.datetime(2022, 1, 1),
          tags=['nba_database'])

t1 = PythonOperator(
    task_id='run_teams',
    python_callable=run_teams,
    op_kwargs=kwargs,
    dag=dag
)
