# db.py
import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='predicciones_db',   # Nombre de la base de datos
            user='root',              # Usuario root
            password=''               # Sin contraseña
        )

        if connection.is_connected():
            print("Conexión a la base de datos 'asistencias' establecida.")
            return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def cerrar_conexion(connection):
    if connection.is_connected():
        connection.close()
        print("Conexión cerrada.")
