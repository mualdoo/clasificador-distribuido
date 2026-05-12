import csv

archivo_gigante = '/media/aldo/Data/Arxiv/archive/dataset_arxiv_limpio.csv'
archivo_perfecto = '/media/aldo/Data/Arxiv/archive/dataset_arxiv_balance.csv'

# ¿Cuántos documentos máximos queremos por categoría padre?
# 20,000 es un número excelente para entrenar modelos de texto.
LIMITE_POR_CATEGORIA = 20000 

conteos = {}
guardados = 0

print("Leyendo el archivo gigante y equilibrando las fuerzas de la ciencia...")

with open(archivo_gigante, 'r', encoding='utf-8') as f_in, \
     open(archivo_perfecto, 'w', newline='', encoding='utf-8') as f_out:
    
    lector = csv.reader(f_in)
    escritor = csv.writer(f_out)
    
    # Escribimos las cabeceras
    cabeceras = next(lector)
    escritor.writerow(cabeceras)
    
    for fila in lector:
        if len(fila) < 2:
            continue
            
        categoria_compuesta = fila[0]
        # Extraemos el padre (ej. "Fisica" de "Fisica|Astro")
        cat_padre = categoria_compuesta.split('|')[0]
        
        # Inicializamos el contador si es una categoría nueva
        if cat_padre not in conteos:
            conteos[cat_padre] = 0
            
        # Si aún no llegamos al límite de esta categoría, guardamos el documento
        if conteos[cat_padre] < LIMITE_POR_CATEGORIA:
            escritor.writerow(fila)
            conteos[cat_padre] += 1
            guardados += 1

print("\n¡Balanceo terminado!")
print("-" * 30)
for cat, cantidad in conteos.items():
    print(f"{cat}: {cantidad} documentos")
print("-" * 30)
print(f"Total en el nuevo dataset: {guardados} documentos.")