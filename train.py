import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# 1. Cargar el dataset temporal
df = pd.read_csv("/home/aldo/.cache/kagglehub/datasets/sumitm004/arxiv-scientific-research-papers-dataset/versions/2/arXiv_scientific dataset.csv")

# 2. Limpieza básica y adaptación de etiquetas
df = df.dropna(subset=['category_code'])
df['title'] = df['title'].fillna('')
df['summary'] = df['summary'].fillna('')

df['label'] = df['category_code'].astype(str).str.replace('.', '/', regex=False)
df['texto_completo'] = df['title'] + " " + df['summary']

# --- NUEVO: FILTRADO Y BALANCEO ---

# A) Tomar solo las 15 categorías con más registros
top_15_categorias = df['label'].value_counts().nlargest(15).index
df = df[df['label'].isin(top_15_categorias)]

# B) Limitar a máximo 500 registros por categoría (Forma segura)
# 1. Mezclamos todas las filas al azar (frac=1) con una semilla fija (random_state=42)
# 2. Agrupamos por 'label' y tomamos las primeras 500 filas de cada grupo
df = df.sample(frac=1, random_state=42).groupby('label').head(500)

print("\nDistribución final de datos por categoría:")
print(df['label'].value_counts())

# ----------------------------------

# 3. Definir características (X) y objetivo (y)
X = df['texto_completo'] 
y = df['label']

# 4. Crear, ajustar y guardar el LabelEncoder
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Guardamos el encoder (ENCODER_PATH)
with open("encoder.pkl", "wb") as f:
    pickle.dump(encoder, f)
print(f"Encoder guardado. Total de clases: {len(encoder.classes_)}")

# 5. Dividir los datos en entrenamiento (80%) y prueba (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# 6. Construir el Pipeline de Machine Learning
# Usamos TF-IDF para convertir el texto a números y Regresión Logística como clasificador.
# La Regresión Logística soporta 'predict_proba' nativamente.
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(stop_words='english', max_features=10000)),
    ('classifier', LogisticRegression(max_iter=1000))
])

# 7. Entrenar el modelo
print("Entrenando el modelo (esto puede tomar unos segundos)...")
pipeline.fit(X_train, y_train)

# 8. Evaluar el modelo
print("\nEvaluando el modelo con los datos de prueba:")
y_pred = pipeline.predict(X_test)
# classification_report mostrará la precisión, recall y f1-score por clase
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

# 9. Guardar el modelo completo (MODEL_PATH)
# Al guardar el pipeline entero, el vectorizador se guarda junto con el clasificador.
with open("model.pkl", "wb") as f:
    pickle.dump(pipeline, f)
print("\n¡Modelo 'model.pkl' guardado con éxito!")


# df = pd.read_csv("/home/aldo/.cache/kagglehub/datasets/sumitm004/arxiv-scientific-research-papers-dataset/versions/2/arXiv_scientific dataset.csv")
