from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
import psycopg2
import pandas as pd
import folium

POSTGRESQL_HOST = 'localhost'
POSTGRESQL_PORT = '5432'
POSTGRESQL_USER = 'shoun1'
POSTGRESQL_DBNAME = 'amb_info'
POSTGRESQL_PASSWORD = '2003shAD@'

conn = psycopg2.connect(
    host=POSTGRESQL_HOST,
    port=POSTGRESQL_PORT,
    user=POSTGRESQL_USER,
    dbname = POSTGRESQL_DBNAME,
    password=POSTGRESQL_PASSWORD
)

cur = conn.cursor()

def update_ambulancestatus():
    query1 = "SELECT ambulance_id,status FROM assignments;" #query
    cur.execute(query1)
    query2 = "SELECT amb_id,status FROM ambulances;"
    cur.execute(query2)
    res1 = cur.fetchall()
    res2 = cur.fetchall()
    #create dictionaries to map amb ids to statuses
    assignment_status = {row[0]:row[1] for row in res1}
    ambulance_status = {row[0]:row[1] for row in res2}
    for ambulance_id,new_status in assignment_status.items():
        if ambulance_id in assignment_status:
            new_status = assignment_status[ambulance_id]
            addcol_query = "ALTER TABLE ambulances ADD COLUMN new_status SERIAL;"
            cur.execute(addcol_query)
            update_query = "UPDATE ambulances SET status=new_status WHERE amb_id = amb_id;"
            cur.execute(update_query)
    query3 = "SELECT * FROM ambulances;"
    cur.execute(query3)
    res = cur.fetchall()
    print(res)
update_ambulancestatus()

def track_ambulancelocation():
    query = "SELECT ambulance_id,latitude,longitude FROM tracking_data;"
    cur.execute(query)
    current_loc = cur.fetchall()
    for row in current_loc:
        ambulance_id = row[0]
        latitude = row[1]
        longitude = row[2]
        gps_locator()
        try:
            print("Ambulance id: ",ambulance_id)
            print("Current location: ",latitude,longitude)
            folium.Marker([latitude,longitude],popup='current location')
        except:
            print("Internet not available")

def gps_locator():
    obj = folium.Map(location=[0,0],zoom_start=2)

default_args = {
    'owner':'shoun10',
    'start_date' : datetime.datetime(2023,07,18),
    'retries' : 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

with DAG(
    'ambulance tracker',
    default_args=default_args,
    schedule_interval = timedelta(days=1),
    catchup=False
) as dag:

update_ambulancestatus_task = PythonOperator(
    task_id = 'update_ambulancestatus',
    python_callable=update_ambulancestatus,
    dag=dag
)

track_ambulancelocations_task = PythonOperator(
    task_id = 'track_ambulancelocation',
    python_callable=track_ambulancelocation,
    dag=dag
)



