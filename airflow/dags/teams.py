import datetime as dt
import sys
sys.path.append('.')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from endpoint.teams import run_teams


target_table = 'teams'
primary_key = 'team_season_id'
conn = MySqlHook(mysql_conn_id='nba_database', schema='nba').get_conn()

default_args = {
    'owner': 'airflow'
}


dag = DAG('teams',
          default_args=default_args,
          description='A DAG scraping the latest teams scripts',
          schedule_interval='0 0 * * *',
          start_date=dt.datetime(2022, 2, 22),
          tags=['nba_database'])

t1 = PythonOperator(
    task_id='run_teams',
    python_callable=run_teams,
    op_kwargs={'target_table': target_table,
               'primary_key': primary_key,
               'conn': conn},
    dag=dag
)
