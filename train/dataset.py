import pandas as pd
import kagglehub

# Download latest version
# path = kagglehub.dataset_download("sumitm004/arxiv-scientific-research-papers-dataset")

# print("Path to dataset files:", path)

# 1. Cargar el dataset (ajusta el nombre al de tu archivo)
df = pd.read_csv('/home/aldo/.cache/kagglehub/datasets/sumitm004/arxiv-scientific-research-papers-dataset/versions/2/arXiv_scientific dataset.csv')

# 2. Limpiar las categorías: Nos quedamos solo con la primera etiqueta
# Ejemplo: "cs.AI cs.LG" -> "cs.AI"
# df['primary_tag'] = df['category'].apply(lambda x: x.split()[0])

# 3. Ver cuáles son las más frecuentes
print("📊 Top 16 categorías más frecuentes:")
print(df['category'].value_counts().head(16))