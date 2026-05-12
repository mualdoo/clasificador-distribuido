import logging

class MessageHandler:
    def __init__(self):
        # Diccionario para mapear tipos de mensaje a funciones
        self._routes = {}

    def registrar(self, tipo_mensaje: str, funcion_handler):
        """
        Registra una función de lógica de negocio para un tipo de mensaje.
        La función debe aceptar un diccionario (payload) y retornar un diccionario (respuesta).
        """
        self._routes[tipo_mensaje] = funcion_handler

    def procesar(self, mensaje: dict) -> dict:
        """
        Recibe el mensaje entrante, busca si hay una función registrada para él,
        la ejecuta y retorna la respuesta.
        """
        tipo = mensaje.get("tipo")
        payload = mensaje.get("payload", {})

        if not tipo:
            return {"status": "error", "error": "El mensaje no tiene un campo 'tipo'"}

        funcion = self._routes.get(tipo)
        if not funcion:
            logging.warning(f"No hay handler registrado para el tipo de mensaje: {tipo}")
            return {"status": "error", "error": f"Tipo de mensaje '{tipo}' desconocido"}

        try:
            # Ejecutamos tu lógica de negocio
            resultado = funcion(payload)
            return {"status": "ok", "data": resultado}
        except Exception as e:
            logging.error(f"Error procesando mensaje '{tipo}': {str(e)}")
            return {"status": "error", "error": str(e)}