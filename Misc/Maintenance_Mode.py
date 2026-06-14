'''

Author : Arvinder
Data Queried : Next 24hours
KB's
https://www.geeksforgeeks.org/get-column-names-from-postgresql-table-using-psycopg2/
https://pynative.com/python-cursor-fetchall-fetchmany-fetchone-to-read-rows-from-table/

'''

##### Start #####

## Import Modules
import psycopg2
import os
import time
from datetime import datetime,timedelta
import csv
import keyring

## Script Start Time
print(f"Start Time : ",datetime.now().strftime("%Y-%m-%d %H-%M-%S"))

## Define Empty Lists
final_cm_data = []
final_report_data = []

## Function for Creating Empty CSV File
def Create_File(name):
    file_name = str(name + ".csv")
    if os.path.exists(file_name):
        # Delete if file already present
        print("{} File is present, deleting and re-creating empty".format(file_name))
        os.remove(file_name)
        # Induce Delay
        time.sleep(3)
        # Create New File
        new_file = open(file_name,"x")
        csv.writer(new_file)
        new_file.close()
   
    else:
        print("{} File is not present, creating new & empty".format(file_name))
        # Create New File
        new_file = open(file_name,"x")
        csv.writer(new_file)
        new_file.close()

## Function to Get Change Tickets based on APP Name
def get_data(name):
    try:
        connection = psycopg2.connect(
        database="dbname",
        user="userid",
        password = '',
        host="db-name.rds.amazonaws.com",
        port="5432") # this is the port usually for postgresql
        cursor = connection.cursor()
        print ("Connection Established")
        name = "'" + name + "'"
        sql_query = """ select 
                        nbr,
                        item_id,
                        item_name
                        from db.table1
                        where
                        item_name like """ + str(name) + """ """
        
        cursor.execute(sql_query)
        return cursor.fetchall()

    except:
        print("Error : Failed to establish connection")

    finally:
        if (connection):
            connection.close()
            cursor.close()
            print("Connection Closed")
       
## Get Details
final_data = get_data("server%123%")

## Create Empty File with headers
Create_File("file_name")
time.sleep(2)
values = open("file_name.csv",'w',newline='')
header = ['NUMBER','NAME','some more here....']
csv.writer(values).writerow(header)

## Establish Connection Again
connection = psycopg2.connect(
        database="tmodspgdb",
        user="srv1234",
        password = '',
        host="ei-ft-prod-tmods-db-cluster.cluster-ro-cm8z5npw7ana.us-east-1.rds.amazonaws.com",
        port="5432")

## Define Datetime
'''
delta = timedelta(days=-90)
start_date = (datetime.now() + delta).strftime("%Y-%m-%d")
start_date = "'" + start_date + "'"
end_date = datetime.now().strftime("%Y-%m-%d")
end_date = "'" + end_date + "'" '''

delta = timedelta(hours=24)
start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
start_date = "'" + start_date + "'"
end_date = (datetime.now() + delta).strftime("%Y-%m-%d %H:%M:%S")
end_date = "'" + end_date + "'"

for final_cm in final_cm_data:
    number = final_cm[0]
    number_query = "'" + number + "'"
    Application_name = final_cm[2]

    sql_query = """ select
                nbr,
                planned_start_ts,
                somemore
                from db.table1
                where
                nbr=""" + str() + """
                AND
                change_environment_cd='Production'
                AND
                change_planned_start_ts BETWEEN
                """ + str(start_date) + """ AND """ + str(end_date) + """ 
                """
    
    cursor = connection.cursor()
    cursor.execute(sql_query)
    row = cursor.fetchone()
    #print(row)
    if row is not None:
        row_data = [row[0],Application_name,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        print(row)
        csv.writer(number).writerow(row_data)
    
## Close Connection & CSV File
connection.close()
cursor.close()
number.close() # csv fule

## Script Start Time
print(f"Start Time : ",datetime.now().strftime("%Y-%m-%d %H-%M-%S"))

##### End #####
