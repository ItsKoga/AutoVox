import mysql.connector
from mysql.connector import Error


import os

def create_connection():
    # Create a connection to the MySQL database
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
    except Error as e:
        return e
    return connection

def execute_query(query):
    connection = create_connection()
    # Execute a query on the MySQL database
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        close_connection(connection)
        return True
    except Error as e:
        close_connection(connection)
        return e
    
def execute_read_query(query):
    connection = create_connection()
    # Execute a read query on the MySQL database
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        close_connection(connection)
        return result
    except Error as e:
        close_connection(connection)
        return e
    
def check_database():
    connection = create_connection()
    # Check if the database is connected
    try:
        if connection.is_connected():
            close_connection(connection)
            return True
        else:
            return connection
    except:
        return False
    
def close_connection(connection):
    # Close the connection to the MySQL database
    connection.close()