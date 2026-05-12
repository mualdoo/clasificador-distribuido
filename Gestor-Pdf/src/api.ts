// api.ts - Utilidades para llamadas a la API

const API_BASE_URL = 'http://localhost:8000'; // Ajusta según tu configuración

// Helper para manejar respuestas
async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// ─── Autenticación ───────────────────────────────────────────────────────────

export async function register(username: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/auth/registro`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ 
      nombre: username,  
      contrasena: password,    
      intereses: []         
    }),
  });
  return handleResponse(response);
}

export async function login(username: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ 
      nombre: username,      
      contrasena: password   
    }),
  });
  return handleResponse(response);
}

export async function logout() {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  });
  return handleResponse(response);
}

export async function getProfile() {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    credentials: 'include',
  });
  return handleResponse(response);
}

// ─── Archivos ────────────────────────────────────────────────────────────────

export async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/archivos/`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });
  return handleResponse(response);
}

export async function getFiles() {
  const response = await fetch(`${API_BASE_URL}/archivos/`, {
    credentials: 'include',
  });
  return handleResponse(response);
}

export async function downloadFile(fileId: string) {
  const response = await fetch(`${API_BASE_URL}/archivos/${fileId}/descargar`, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.blob();
}

export async function deleteFile(fileId: string) {
  const response = await fetch(`${API_BASE_URL}/archivos/${fileId}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  return handleResponse(response);
}

// ─── Administración ──────────────────────────────────────────────────────────

export async function getNodes() {
  const response = await fetch(`${API_BASE_URL}/admin/nodos`, {
    credentials: 'include',
  });
  return handleResponse(response);
}

export async function pingNodes(ip: string) {
  const response = await fetch(`${API_BASE_URL}/admin/ping?ip=${ip}`, {
    method: 'POST',
    credentials: 'include',
  });
  return handleResponse(response);
}

export async function getUsers() {
  const response = await fetch(`${API_BASE_URL}/admin/usuarios`, {
    credentials: 'include',
  });
  return handleResponse(response);
}

export async function deleteUser(userId: string) {
  const response = await fetch(`${API_BASE_URL}/admin/usuarios/${userId}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  return handleResponse(response);
}

export async function getLocations() {
  const response = await fetch(`${API_BASE_URL}/admin/ubicaciones`, {
    credentials: 'include',
  });
  return handleResponse(response);
}

export async function updateUserRole(userId: string, newRole: string) {
  const response = await fetch(`${API_BASE_URL}/admin/usuarios/${userId}/rol`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ rol: newRole }),
  });
  return handleResponse(response);
}

export async function updateUserPassword(userId: string, newPassword: string) {
  const response = await fetch(`${API_BASE_URL}/admin/usuarios/${userId}/password`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ contrasena: newPassword }),
  });
  return handleResponse(response);
}

export async function adminCreateUser(username: string, password: string, role: string) {
  const response = await fetch(`${API_BASE_URL}/admin/usuarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ nombre: username, contrasena: password, rol: role, intereses: [] }),
  });
  return handleResponse(response);
}