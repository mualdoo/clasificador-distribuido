import fitz  # PyMuPDF
import re
import logging
import joblib
from backend.config import MODEL_PATH, ENCODER_PATH

class ClasificadorService:
    def __init__(self):
        self.modelos_cargados = False
        
        # Herramientas del Validador Integradas
        self.patron_doi = re.compile(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', re.IGNORECASE)
        self.palabras_inicio = ['abstract', 'resumen', 'keywords', 'palabras clave']
        self.palabras_final = ['references', 'bibliography', 'referencias', 'literatura citada']
        
        try:
            self.modelo = joblib.load(MODEL_PATH)
            self.vectorizador = joblib.load(ENCODER_PATH)
            self.modelos_cargados = True
            logging.info("Motor de IA y Validador cargados correctamente.")
        except Exception as e:
            logging.error(f"Error al cargar el modelo de IA: {str(e)}")

    def procesar_documento(self, contenido_bytes: bytes, categorias_permitidas: list = None) -> dict:
        """
        Abre el PDF UNA SOLA VEZ. 
        Paso 1: Valida su longitud.
        Paso 2: Extrae texto del inicio y final.
        Paso 3: Valida su estructura científica.
        Paso 4: Si es válido, lo clasifica con IA.
        """
        texto_inicio_bruto = ""
        texto_final_bruto = ""
        
        # ==========================================
        # FASE 1: EXTRACCIÓN ÚNICA Y FILTRO DE TAMAÑO
        # ==========================================
        try:
            with fitz.open(stream=contenido_bytes, filetype="pdf") as doc:
                total_paginas = len(doc)
                
                # Filtro Cadenero
                if total_paginas < 2 or total_paginas > 60:
                    return {"es_valido": False, "razon": f"Longitud atípica ({total_paginas} páginas)."}

                # Extraer Inicio (Para validación y para la IA)
                for num in range(min(2, total_paginas)):
                    texto_inicio_bruto += doc[num].get_text()

                # Extraer Final (Solo para buscar referencias)
                inicio_busqueda_final = max(0, total_paginas - 3)
                for num in range(inicio_busqueda_final, total_paginas):
                    texto_final_bruto += doc[num].get_text()
                    
        except Exception as e:
            return {"es_valido": False, "razon": f"Archivo corrupto o ilegible: {str(e)}"}

        # ==========================================
        # FASE 2: VALIDACIÓN ESTRUCTURAL
        # ==========================================
        puntaje_cientifico = 0
        texto_inicio_lower = texto_inicio_bruto.lower()
        texto_final_lower = texto_final_bruto.lower()

        # Check 1: DOI
        if self.patron_doi.search(texto_inicio_lower):
            puntaje_cientifico += 3
            
        # Check 2: Abstract
        if any(palabra in texto_inicio_lower for palabra in self.palabras_inicio):
            puntaje_cientifico += 2
            
        # Check 3: Referencias
        if any(palabra in texto_final_lower for palabra in self.palabras_final):
            puntaje_cientifico += 2

        if puntaje_cientifico < 4:
            return {"es_valido": False, "razon": "Estructura no científica. Faltan referencias o abstract."}

        # ==========================================
        # FASE 3: CLASIFICACIÓN POR IA
        # ==========================================
        # Reutilizamos el texto del inicio que ya sacamos, lo limpiamos y lo pasamos al modelo
        texto_limpio_ia = re.sub(r'\W+', ' ', texto_inicio_bruto).lower().strip()
        resultado_ia = self._ejecutar_prediccion(texto_limpio_ia, categorias_permitidas)

        # Filtro de Confianza de IA
        if resultado_ia["confianza"] < 25.0:
            return {"es_valido": False, "razon": "El contenido no coincide con literatura científica conocida por la red."}

        # Si sobrevivió a todo, lo devolvemos con luz verde y sus etiquetas
        return {
            "es_valido": True,
            "razon": "Documento validado y clasificado con éxito.",
            "clasificacion": resultado_ia
        }

    def _ejecutar_prediccion(self, texto_limpio: str, categorias_permitidas: list = None) -> dict:
        """
        Método interno (privado) que solo hace la matemática de predicción.
        Contiene exactamente la misma lógica de marginalización que hicimos antes.
        """
        if not self.modelos_cargados or not texto_limpio:
            return {"categoria": "General", "subcategoria": "Variado", "confianza": 0.0}

        try:
            texto_vectorizado = self.vectorizador.transform([texto_limpio])
            
            if hasattr(self.modelo, "predict_proba"):
                calificaciones = self.modelo.predict_proba(texto_vectorizado)[0]
                es_porcentaje = True
            else:
                calificaciones = self.modelo.decision_function(texto_vectorizado)[0]
                es_porcentaje = False

            todas_las_clases = self.modelo.classes_
            probabilidad_por_padre = {}
            mejor_subcategoria_por_padre = {}
            max_puntaje_subcat = {}

            for clase, puntaje in zip(todas_las_clases, calificaciones):
                cat_padre = clase.split('|')[0] if '|' in clase else clase
                subcat = clase.split('|')[1] if '|' in clase else 'General'

                if categorias_permitidas and (cat_padre not in categorias_permitidas):
                    continue

                if cat_padre not in probabilidad_por_padre:
                    probabilidad_por_padre[cat_padre] = 0.0
                    max_puntaje_subcat[cat_padre] = -float('inf')
                    mejor_subcategoria_por_padre[cat_padre] = 'General'

                probabilidad_por_padre[cat_padre] += puntaje

                if puntaje > max_puntaje_subcat[cat_padre]:
                    max_puntaje_subcat[cat_padre] = puntaje
                    mejor_subcategoria_por_padre[cat_padre] = subcat

            if not probabilidad_por_padre:
                return {"categoria": "Sin Coincidencia", "subcategoria": "N/A", "confianza": 0.0}

            padre_ganador = max(probabilidad_por_padre, key=probabilidad_por_padre.get)
            subcat_ganadora = mejor_subcategoria_por_padre[padre_ganador]
            confianza_padre = probabilidad_por_padre[padre_ganador]

            confianza_final = round(confianza_padre * 100, 2) if es_porcentaje else round(confianza_padre, 2)
            confianza_final = min(100.0, confianza_final)

            return {
                "categoria": padre_ganador,
                "subcategoria": subcat_ganadora,
                "confianza": confianza_final
            }
            
        except Exception as e:
            logging.error(f"Error durante la matemática de clasificación: {str(e)}")
            return {"categoria": "Error", "subcategoria": "Error", "confianza": 0.0}