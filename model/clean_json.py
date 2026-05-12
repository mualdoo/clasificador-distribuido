import json
import csv

archivo_entrada = '/media/aldo/Data/Arxiv/archive/arxiv-metadata-oai-snapshot.json'
archivo_salida = '/media/aldo/Data/Arxiv/archive/dataset_arxiv_limpio.csv'

# Mapeo para que las categorías padre sean legibles
mapeo_categorias = {
    'cs': 'Computacion',
    'math': 'Matematicas',
    'physics': 'Fisica',
    'q-bio': 'Biologia',
    'q-fin': 'Finanzas',
    'stat': 'Estadistica',
    'eess': 'Ingenieria',
    'econ': 'Economia'
}

# arXiv tiene sub-ramas de física muy antiguas que no usan el formato con punto
fisica_historica = ['hep-ph', 'hep-th', 'hep-ex', 'hep-lat', 'gr-qc', 'quant-ph', 'astro-ph', 'nucl-th', 'nucl-ex']

print("Iniciando extracción jerárquica por línea...")

with open(archivo_entrada, 'r', encoding='utf-8') as f_in, \
     open(archivo_salida, 'w', newline='', encoding='utf-8') as f_out:
    
    escritor_csv = csv.writer(f_out)
    escritor_csv.writerow(['categoria', 'resumen']) # Cabeceras
    
    procesados = 0
    guardados = 0
    
    for linea in f_in:
        procesados += 1
        try:
            doc = json.loads(linea)
            
            # Tomamos la primera categoría reportada (la principal)
            cat_cruda = doc.get('categories', '').split(' ')[0]
            
            # Separamos en Categoría y Subcategoría
            if '.' in cat_cruda:
                partes = cat_cruda.split('.', 1)
                cat_padre = partes[0]
                subcat = partes[1]
            else:
                cat_padre = cat_cruda
                subcat = 'General' # Si no tiene subcategoría, le asignamos 'General'
            
            # Formateamos la etiqueta compuesta usando el separador '|'
            if cat_padre in mapeo_categorias:
                etiqueta_compuesta = f"{mapeo_categorias[cat_padre]}|{subcat}"
            elif cat_padre in fisica_historica:
                etiqueta_compuesta = f"Fisica|{cat_padre}"
            else:
                continue # Ignoramos ramas raras para mantener la calidad del modelo
                
            resumen = doc.get('abstract', '').replace('\n', ' ').strip()
            
            if resumen:
                escritor_csv.writerow([etiqueta_compuesta, resumen])
                guardados += 1
                
        except json.JSONDecodeError:
            continue
            
        if procesados % 100000 == 0:
            print(f"Líneas escaneadas: {procesados} | Documentos extraídos: {guardados}")

print(f"\n¡Extracción terminada! Se guardaron {guardados} documentos jerárquicos en {archivo_salida}")