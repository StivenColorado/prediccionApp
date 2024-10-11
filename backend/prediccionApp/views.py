from django.shortcuts import render
from django.http import JsonResponse
from .db_connection import obtener_conexion, cerrar_conexion
from mysql.connector import Error  

def index(request):
    return render(request, 'index.html')  # Ruta al template


def obtener_encuestas(request):
    connection = obtener_conexion()
    encuestas = []

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM encuestas")  # Ajusta la consulta según tus necesidades
            rows = cursor.fetchall()
            
            # Obtén los nombres de las columnas
            column_names = [desc[0] for desc in cursor.description]

            for row in rows:
                encuestas.append(dict(zip(column_names, row)))

            cursor.close()
        except Error as e:
            print(f"Error al realizar la consulta: {e}")
        finally:
            cerrar_conexion(connection)

    return JsonResponse(encuestas, safe=False)
