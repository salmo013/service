import mysql.connector

db_conn = mysql.connector.connect(host="3.21.10.177", user="API", 
password="password", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
 DROP TABLE door_motion, motion
''')
db_conn.commit()
db_conn.close()