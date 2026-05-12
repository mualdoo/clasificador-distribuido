import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
import joblib

ruta_csv = '/media/aldo/Data/Arxiv/archive/dataset_arxiv_limpio.csv'

# 1. Escaneo rápido para encontrar todas las etiquetas compuestas únicas
print("Escaneando el CSV para identificar todas las categorías y subcategorías...")
# Leemos solo la columna 'categoria' para no saturar la RAM
df_clases = pd.read_csv(ruta_csv, usecols=['categoria'])
clases_posibles = df_clases['categoria'].unique()
print(f"Se encontraron {len(clases_posibles)} combinaciones únicas de Categoría|Subcategoría.")
del df_clases # Liberamos memoria inmediatamente

# 2. Configuración del Vectorizador y el Modelo
print("\nConfigurando motor de IA...")
# max_features asegura que la huella de memoria se mantenga baja
vectorizador = HashingVectorizer(n_features=2**18, stop_words='english', alternate_sign=False)
modelo = SGDClassifier(loss='hinge', random_state=42)

# 3. Entrenamiento por lotes (Chunking)
tamano_lote = 50000
print(f"Iniciando entrenamiento por lotes de {tamano_lote} documentos...")

lotes = pd.read_csv(ruta_csv, chunksize=tamano_lote)

for i, lote in enumerate(lotes):
    # Aseguramos que el texto sea String y limpiamos posibles nulos
    X_texto = lote['resumen'].astype(str).fillna('')
    y_etiquetas = lote['categoria']
    
    # Transformación matemática
    X_vectorizado = vectorizador.transform(X_texto)
    
    # Aprendizaje incremental
    modelo.partial_fit(X_vectorizado, y_etiquetas, classes=clases_posibles)
    
    print(f" Lote {i+1} procesado y aprendido.")

# 4. Guardado de los pesos y el cerebro
print("\nEntrenamiento finalizado. Guardando archivos .pkl...")
joblib.dump(modelo, 'clasificador_nodos.pkl')
joblib.dump(vectorizador, 'vectorizador_nodos.pkl')

print("¡Éxito! Archivos generados: 'clasificador_nodos.pkl' y 'vectorizador_nodos.pkl'")