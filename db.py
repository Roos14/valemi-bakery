# db.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          
        password="root",  
        database="valemi_bakery"    
    )