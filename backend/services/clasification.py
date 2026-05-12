import fitz  # PyMuPDF
import re
import logging
import joblib
from backend.config import MODEL_PATH, ENCODER_PATH
import time

class ClasificadorService:
    def __init__(self):
        """
        Inicializa el servicio y carga el modelo de IA en la RAM.
        Esto debe hacerse solo una vez al arrancar el servidor para no ralentizar las peticiones.
        """
        self.modelos_cargados = False
        try:
            self.modelo = joblib.load(MODEL_PATH)
            self.vectorizador = joblib.load(ENCODER_PATH)
            self.modelos_cargados = True
            logging.info("Modelo de clasificación IA cargado correctamente.")
        except FileNotFoundError:
            logging.warning("No se encontraron los archivos .pkl del modelo. La clasificación automática devolverá 'Sin Categoría'.")
        except Exception as e:
            logging.error(f"Error al cargar el modelo de IA: {str(e)}")

    def extraer_texto_memoria(self, contenido_bytes: bytes, max_paginas: int = 5) -> str:
        """
        Extrae el texto de un PDF que se encuentra directamente en la memoria RAM (bytes).
        Lee solo las primeras páginas para optimizar la velocidad y el uso de CPU.
        """
        texto_extraido = ""
        try:
            # El secreto de PyMuPDF: usar 'stream' para leer los bytes en lugar de una ruta de archivo
            with fitz.open(stream=contenido_bytes, filetype="pdf") as doc:
                # Limitamos la lectura a 'max_paginas' o al total del documento, lo que sea menor
                paginas_a_leer = min(max_paginas, len(doc))
                
                for num_pagina in range(paginas_a_leer):
                    texto_extraido += doc[num_pagina].get_text()
                    
            # Limpieza básica: quitar saltos de línea, caracteres especiales y pasar a minúsculas
            texto_limpio = re.sub(r'\W+', ' ', texto_extraido).lower().strip()
            return texto_limpio
            
        except Exception as e:
            logging.error(f"Error al extraer texto del PDF en memoria: {str(e)}")
            return ""

    def predecir_categoria(self, texto_limpio: str) -> dict:
        """
        Devuelve un diccionario con los dos niveles de clasificación.
        """
        if not self.modelos_cargados or not texto_limpio:
            return {"categoria": "General", "subcategoria": "Variado"}

        try:
            texto_vectorizado = self.vectorizador.transform([texto_limpio])
            prediccion_compuesta = self.modelo.predict(texto_vectorizado)[0] 
            
            # prediccion_compuesta será algo como "Fisica|Astrofisica"
            
            if "|" in prediccion_compuesta:
                partes = prediccion_compuesta.split("|")
                return {
                    "categoria": partes[0],       # Ej: "Fisica"
                    "subcategoria": partes[1]     # Ej: "Astrofisica"
                }
            else:
                return {
                    "categoria": prediccion_compuesta,
                    "subcategoria": "General"
                }
            
        except Exception as e:
            import logging
            logging.error(f"Error durante la clasificación: {str(e)}")
            return {"categoria": "Error", "subcategoria": "Error"}
