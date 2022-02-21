FROM apache/airflow:2.2.3
USER airflow
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

COPY /data .
