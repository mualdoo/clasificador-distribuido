import fitz  # PyMuPDF
import io

def extract_text_from_bytes(pdf_bytes):
    """
    Extrae el texto de un archivo PDF recibido en formato de bytes.
    Ideal para procesar archivos subidos vía API sin guardarlos en disco primero.
    """
    text = ""
    try:
        # Abrimos el PDF desde el flujo de bytes
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            # Extraemos texto de cada página
            for page in doc:
                text += page.get_text()
        
        # Limpieza básica para mejorar la clasificación
        text = clean_text(text)
        
        return text if text.strip() else None
    
    except Exception as e:
        print(f"❌ Error al extraer texto del PDF: {e}")
        return None

def clean_text(text):
    """
    Realiza una limpieza ligera del texto para eliminar ruidos comunes 
    en PDFs científicos (saltos de línea extraños, espacios múltiples).
    """
    if not text:
        return ""
    
    # Unimos palabras cortadas por guiones al final de la línea
    text = text.replace("-\n", "")
    
    # Reemplazamos saltos de línea y tabulaciones por espacios
    text = text.replace("\n", " ").replace("\t", " ")
    
    # Eliminamos espacios múltiples
    text = " ".join(text.split())
    
    return text

def extract_text_from_file(file_path):
    """
    Función de utilidad por si necesitas procesar un archivo 
    que ya existe físicamente en el servidor.
    """
    try:
        with open(file_path, "rb") as f:
            return extract_text_from_bytes(f.read())
    except Exception as e:
        print(f"❌ Error al abrir el archivo: {e}")
        return None

# Prueba rápida del extractor
if __name__ == "__main__":
    # Puedes probarlo con un PDF local si tienes uno a la mano
    # path = "ruta/a/tu/paper.pdf"
    # print(extract_text_from_file(path)[:500]) # Muestra los primeros 500 caracteres
    pass