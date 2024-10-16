from django.shortcuts import render
from django.http import JsonResponse
from .db_connection import obtener_conexion, cerrar_conexion
from mysql.connector import Error
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.cluster import KMeans
import numpy as np

def index(request):
    return render(request, 'index.html')

def obtener_encuestas(request):
    connection = obtener_conexion()
    encuestas = []
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM encuestas")
            rows = cursor.fetchall()
            
            column_names = [desc[0] for desc in cursor.description]
            
            for row in rows:
                encuestas.append(dict(zip(column_names, row)))
            
            cursor.close()
        except Error as e:
            print(f"Error al realizar la consulta: {e}")
        finally:
            cerrar_conexion(connection)
    
    return JsonResponse(encuestas, safe=False)

def obtener_datos_encuestas():
    connection = obtener_conexion()
    if connection:
        try:
            query = "SELECT * FROM encuestas"
            df = pd.read_sql(query, connection)
            return df
        except Error as e:
            print(f"Error al obtener datos: {e}")
            return None
        finally:
            cerrar_conexion(connection)
    return None

def predecir_recomendacion(request):
    df = obtener_datos_encuestas()
    
    if df is None or df.empty:
        return JsonResponse({'error': 'No se pudieron obtener los datos de encuestas.'}, status=500)

    # Preparar resultados
    resultados = {
        'estadisticas': {},
        'predicciones': {},
        'perfiles': {},
        'satisfaccion': {}
    }

    # 1. Estadísticas generales
    resultados['estadisticas'] = {
        'total_encuestas': int(len(df)),
        'distribucion_edad': df['edad'].value_counts().to_dict(),
        'distribucion_genero': df['genero'].value_counts().to_dict(),
        'canales_preferidos': df['preferencia_atencion'].value_counts().to_dict()
    }

    # 2. Modelo de predicción principal
    features_principales = [
        'calidad_servicio', 
        'satisfaccion_personal', 
        'personal_capacitado',
        'facilidad_canales_digitales', 
        'rapidez_respuesta',
        'resolucion_primer_contacto'
    ]

    X = df[features_principales].copy()
    y = df['recomendaria_banco'].copy()

    # Codificación de variables
    le = LabelEncoder()

    # Aplicar LabelEncoder a X y codificar y
    for column in X.columns:
        if X[column].dtype == 'object':  # Solo aplicar a columnas categóricas
            X[column] = le.fit_transform(X[column])

    # Codificar y y verificar clases
    y = le.fit_transform(y)

    # Verificar clases únicas
    print("Clases de y:", np.unique(y))  # Para depuración, verifica las clases de y

    # Ajustar y si es necesario (si las clases son [1, 2, 3, 4, 5])
    if np.array_equal(np.unique(y), np.array([1, 2, 3, 4, 5])):
        y = y - 1  # Cambiar a [0, 1, 2, 3, 4]

    # Dividir los datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Preprocesamiento y modelo
    numerical_features = ['calidad_servicio', 'satisfaccion_personal', 'personal_capacitado']
    categorical_features = ['facilidad_canales_digitales', 'rapidez_respuesta', 'resolucion_primer_contacto']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(), categorical_features)
        ])

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'))
    ])

    # Definir la cuadrícula de hiperparámetros para la búsqueda
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__learning_rate': [0.01, 0.1, 0.2],
        'classifier__max_depth': [3, 5, 7]
    }

    # Realizar la búsqueda de hiperparámetros con validación cruzada
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    # Obtener el mejor modelo
    best_model = grid_search.best_estimator_

    # Predicciones y evaluación
    y_pred = best_model.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))

    # Importancia de características
    feature_importance = dict(zip(features_principales, 
                                [float(imp) for imp in best_model.named_steps['classifier'].feature_importances_]))

    resultados['predicciones'] = {
        'precision_modelo': accuracy,
        'factores_importantes': feature_importance,
        'predicciones_muestra': [int(pred) for pred in y_pred[:10]]
    }

    # 3. Perfiles de clientes
    features_perfil = ['edad', 'frecuencia_uso', 'preferencia_atencion']
    X_perfil = df[features_perfil].copy()
    
    # Codificar X_perfil
    for column in X_perfil.columns:
        if X_perfil[column].dtype == 'object':  # Solo aplicar a columnas categóricas
            X_perfil[column] = le.fit_transform(X_perfil[column])

    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_perfil)

    # Análisis de perfiles
    df['cluster'] = clusters
    perfiles = {}
    for i in range(3):
        cluster_data = df[df['cluster'] == i]
        perfiles[f'perfil_{i+1}'] = {
            'tamaño': int(len(cluster_data)),
            'edad_comun': cluster_data['edad'].mode()[0],
            'frecuencia_uso_tipica': cluster_data['frecuencia_uso'].mode()[0],
            'preferencia_atencion': cluster_data['preferencia_atencion'].mode()[0]
        }

    resultados['perfiles'] = perfiles

    # 4. Análisis de satisfacción
    resultados['satisfaccion'] = {
        'general': df['satisfaccion_personal'].value_counts().to_dict(),
        'por_edad': {
            str(k): {f"{k} - {satisfaccion}": count for satisfaccion, count in v.items()}
            for k, v in df.groupby('edad')['satisfaccion_personal'].value_counts().groupby(level=0)
        },
        'calidad_servicio': df['calidad_servicio'].value_counts().to_dict(),
        'intencion_cambio': df['cambiar_banco'].value_counts().to_dict()
    }
    
    resultados_serializables = {str(key): value for key, value in resultados.items()}
    print(resultados)  # Agregar esta línea para depuración
    return JsonResponse(resultados_serializables)
