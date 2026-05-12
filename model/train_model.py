import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
import joblib

ruta_csv = '/media/aldo/Data/Arxiv/archive/dataset_arxiv_balance.csv'

print("1. Cargando el dataset completo en memoria...")
# Como el CSV ya está limpio, cabe perfectamente en la RAM de una PC normal
df = pd.read_csv(ruta_csv)

# Nos aseguramos de que no haya filas vacías
df = df.dropna(subset=['resumen', 'categoria'])

print("2. Vectorizando con TF-IDF...")
print("(Esto le dará un peso enorme a palabras raras como 'RNA' o 'Célula')")
# Usamos TF-IDF. max_features=50000 mantiene un vocabulario gigante pero sin explotar la RAM
vectorizador = TfidfVectorizer(max_features=50000, stop_words='english')
X_vectorizado = vectorizador.fit_transform(df['resumen'])

print("3. Entrenando el modelo de IA...")
print("(Aplicando 'class_weight=balanced' para quitarle la obsesión por la Física)")

# Aquí está la magia: 'balanced' obliga a la IA a respetar a las categorías pequeñas
modelo = SGDClassifier(loss='log_loss', class_weight='balanced', random_state=42)

# Entrenamos todo de un solo golpe (fit en lugar de partial_fit)
modelo.fit(X_vectorizado, df['categoria'])

print("\n4. Guardando el cerebro de la IA...")
joblib.dump(modelo, 'clasificador_nodos.pkl')
joblib.dump(vectorizador, 'vectorizador_nodos.pkl')

print("¡Modelo entrenado exitosamente!")