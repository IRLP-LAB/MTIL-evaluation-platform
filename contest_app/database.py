import mysql.connector

# Replace the placeholders with your MySQL connection details
db_config = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'mtil_evaluation_platform'
}
db_conn = mysql.connector.connect(**db_config)
