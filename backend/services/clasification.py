import fitz
import re
import logging
import joblib
from backend.config import MODEL_PATH, ENCODER_PATH

class ClasificadorService:
    def __init__(self):
        self.modelos_cargados = False
        try:
            self.modelo = joblib.load(MODEL_PATH)
            self.vectorizador = joblib.load(ENCODER_PATH)
            self.modelos_cargados = True
            logging.info("Modelo de clasificación IA cargado correctamente.")
        except Exception as e:
            logging.error(f"Error al cargar el modelo de IA: {str(e)}")

    def extraer_texto_memoria(self, contenido_bytes: bytes, max_paginas: int = 5) -> str:
        texto_extraido = ""
        try:
            with fitz.open(stream=contenido_bytes, filetype="pdf") as doc:
                for num_pagina in range(min(max_paginas, len(doc))):
                    texto_extraido += doc[num_pagina].get_text()
            return re.sub(r'\W+', ' ', texto_extraido).lower().strip()
        except Exception:
            return ""

    def predecir_categoria(self, texto_limpio: str, categorias_permitidas: list = None) -> dict:
        """
        Predice la categoría filtrando por los intereses del usuario y devuelve la confianza.
        categorias_permitidas: Lista de strings, ej. ["Computacion", "Fisica"]
        """
        if not self.modelos_cargados or not texto_limpio:
            return {"categoria": "General", "subcategoria": "Variado", "confianza": 0.0}

        try:
            texto_vectorizado = self.vectorizador.transform([texto_limpio])
            
            # Usamos predict_proba para obtener los porcentajes de TODAS las clases
            # Si olvidaste cambiar a 'log_loss', usamos decision_function como respaldo
            if hasattr(self.modelo, "predict_proba"):
                calificaciones = self.modelo.predict_proba(texto_vectorizado)[0]
                es_porcentaje = True
            else:
                calificaciones = self.modelo.decision_function(texto_vectorizado)[0]
                es_porcentaje = False

            todas_las_clases = self.modelo.classes_
            
            mejor_clase = None
            mejor_puntaje = -float('inf')

            # Evaluamos cada clase y su calificación
            for clase, puntaje in zip(todas_las_clases, calificaciones):
                # Extraemos quién es el padre de esta clase (ej. "Fisica" de "Fisica|Astro")
                cat_padre = clase.split('|')[0] if '|' in clase else clase
                
                # FILTRO: Si el usuario dio una lista y esta categoría no está ahí, la ignoramos
                if categorias_permitidas and (cat_padre not in categorias_permitidas):
                    continue
                
                # Nos quedamos con la calificación más alta de las que pasaron el filtro
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_clase = clase

            # Si el usuario mandó un filtro muy estricto y el modelo no encontró nada coherente
            if mejor_clase is None:
                return {"categoria": "Sin Coincidencia", "subcategoria": "N/A", "confianza": 0.0}

            # Darle formato a la confianza
            confianza_final = round(mejor_puntaje * 100, 2) if es_porcentaje else round(mejor_puntaje, 2)

            # Separamos en Categoría y Subcategoría para la respuesta
            if "|" in mejor_clase:
                partes = mejor_clase.split("|")
                return {
                    "categoria": partes[0],
                    "subcategoria": partes[1],
                    "confianza": confianza_final # Regresa un float, ej: 85.45
                }
            else:
                return {
                    "categoria": mejor_clase,
                    "subcategoria": "General",
                    "confianza": confianza_final
                }
            
        except Exception as e:
            logging.error(f"Error durante la clasificación: {str(e)}")
            return {"categoria": "Error", "subcategoria": "Error", "confianza": 0.0}