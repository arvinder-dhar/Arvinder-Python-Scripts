# https://www.geeksforgeeks.org/get-column-names-from-postgresql-table-using-psycopg2/
import psycopg2
from datetime import datetime, timezone

conn = psycopg2.connect(
    database="dbname",
    user="userid",
    password='', # use kyering
    host="PostgreSQLdb-cluster-name.us-east-1.something.com",
    port="something") # for PostgreSQL it is usuall 5432

cur = conn.cursor()

## Get specific column value
sql_query = '''select * from table.column1 where column_value_name='desiredvalue' limit 1'''
cur.execute(sql_query)
values_query = cur.fetchall()
print(values_query)

column_names = [desc[0] for desc in cur.description] 
for i in column_names: 
    print(i) 

cur.close()
conn.close()

sql_query_2 = '''select * from table.column2 where ticket_nbr='12345' '''
cur.execute(sql_query_2)

change_numbers = []
data_columns = []

for value in values_query:
    change_numbers.append(value[0])

for change_number in change_numbers:
    change_number = "'" + change_number + "'"    
    data_columns.append(cur.execute('''select * from table.column2 where ticket_nbr='12345' limit 2'''))
    cur.fetchall()

for data_column in data_columns:
    print(data_column)    
    
cur.close()
conn.close()


