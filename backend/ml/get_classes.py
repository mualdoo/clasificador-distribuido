import joblib

def obtener_lista_completa_categorias():
    print("Cargando el modelo...")
    try:
        # Cargamos el cerebro de la IA
        modelo = joblib.load('model.pkl')
        
        # El atributo classes_ contiene el array con todas las etiquetas conocidas
        todas_las_clases = modelo.classes_
        
        print(f"\nEl modelo fue entrenado para reconocer {len(todas_las_clases)} clasificaciones distintas:\n")
        print("-" * 40)
        
        # Las ordenamos alfabéticamente para que sea más fácil leerlas
        for clase in sorted(todas_las_clases):
            print(clase)
            
        print("-" * 40)
        
    except FileNotFoundError:
        print("Error: No se encontró 'clasificador_nodos.pkl'.")
        
if __name__ == "__main__":
    obtener_lista_completa_categorias()