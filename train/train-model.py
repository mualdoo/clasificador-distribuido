import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

def train():
    df = pd.read_csv('/home/aldo/.cache/kagglehub/datasets/sumitm004/arxiv-scientific-research-papers-dataset/versions/2/arXiv_scientific dataset.csv')
    
    # 1. Limpieza inicial
    df['text'] = df['title'] + " " + df['summary']
    
    # 2. Filtrar categorías con pocos ejemplos (mínimo 400)
    counts = df['category_code'].value_counts()
    valid_codes = counts[counts >= 400].index.tolist()
    df = df[df['category_code'].isin(valid_codes)]
    
    print(f"Entrenando con {len(valid_codes)} categorías que superan los 400 ejemplos.")

    # 3. Crear el mapeo de Código -> Nombre para el motor de inferencia
    # Esto crea un dict como {'cs.LG': 'Machine Learning', ...}
    mapping = df.drop_duplicates('category_code').set_index('category_code')['category'].to_dict()
    
    # 4. Pipeline de entrenamiento
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=10000)),
        ('clf', MultinomialNB())
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        df['text'], df['category_code'], test_size=0.2, random_state=42
    )

    print("Entrenando modelo...")
    pipeline.fit(X_train, y_train)

    # 5. Guardamos el modelo Y el diccionario de nombres en un solo paquete
    model_data = {
        'model': pipeline,
        'mapping': mapping
    }
    joblib.dump(model_data, 'model_v1.joblib')
    print("¡Modelo y Mapeo guardados exitosamente!")

if __name__ == "__main__":
    train()