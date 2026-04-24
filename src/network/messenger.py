import requests
import json
import uuid
from src.config import RPC_PORT

def send_rpc(target_ip, method, params=None):
    """
    Envía una petición JSON-RPC genérica a un nodo destino.
    """
    url = f"http://{target_ip}:{RPC_PORT}/rpc"
    headers = {'content-type': 'application/json'}
    
    payload = {
        "method": method,
        "params": params or {},
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
    }

    try:
        response = requests.post(
            url, data=json.dumps(payload), headers=headers, timeout=5
        ).json()
        
        if "error" in response:
            print(f"Error RPC de {target_ip}: {response['error']}")
            return None
        
        return response.get("result")
    except requests.exceptions.RequestException as e:
        print(f"No se pudo contactar con {target_ip}: {e}")
        return None

def replicate_to_all(nodes_list, method, params):
    """
    Envía una actualización a todos los nodos conocidos en la red.
    """
    results = []
    for node in nodes_list:
        res = send_rpc(node.direccion_ip, method, params)
        results.append(res)
    return results

def request_file_from_node(target_ip, file_uuid):
    """
    Solicita los bytes de un archivo específico a un nodo remoto.
    Recuerda que los bytes vendrán en Base64.
    """
    return send_rpc(target_ip, "get_file_content", {"file_uuid": file_uuid})