import React, { useEffect, useState } from 'react';
import { Folder, Key, Trash2, AlertTriangle, Shield, UserPlus, X } from 'lucide-react';
import { Role, User } from '../types';

import { 
  getUsers, 
  deleteUser as apiDeleteUser,
  updateUserRole,
  updateUserPassword,
  adminCreateUser
} from '../api';

interface Props {
  users: User[];
  onDeleteUser: (id: string) => void;
}

export default function AdminView({ users: initialUsers, onDeleteUser }: Props) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  // Estados para modales
  const [showNewUserModal, setShowNewUserModal] = useState(false);
  const [showPassModal, setShowPassModal] = useState<string | null>(null); 

  // Estados de formularios
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newUserRole, setNewUserRole] = useState<Role>('user');
  const [editPassword, setEditPassword] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      const transformedUsers = data.usuarios.map((u: any) => ({
        id: u.id,
        username: u.nombre, 
        role: u.rol,        
        folders: 0          
      }));
      setUsers(transformedUsers);
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('¿Estás seguro de eliminar este usuario?')) return;
    try {
      await apiDeleteUser(userId);
      setUsers(prev => prev.filter(u => u.id !== userId));
      onDeleteUser(userId);
    } catch (error) {
      console.error('Error al eliminar usuario:', error);
      alert('Error al eliminar el usuario');
    }
  };

  const handleRoleChange = async (userId: string, newRole: Role) => {
    try {
      await updateUserRole(userId, newRole);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (error) {
      console.error('Error al cambiar rol:', error);
      alert('Error al cambiar el rol del usuario');
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername || !newPassword) return alert("Completa los campos");
    try {
      await adminCreateUser(newUsername, newPassword, newUserRole);
      setShowNewUserModal(false);
      setNewUsername('');
      setNewPassword('');
      setNewUserRole('user');
      loadUsers(); 
    } catch (error) {
      console.error('Error al crear usuario:', error);
      alert('Error al crear usuario');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showPassModal || !editPassword) return alert("Ingresa una contraseña");
    try {
      await updateUserPassword(showPassModal, editPassword);
      setShowPassModal(null);
      setEditPassword('');
      alert("Contraseña actualizada exitosamente");
    } catch (error) {
      console.error('Error al cambiar contraseña:', error);
      alert('Error al actualizar la contraseña');
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">Cargando usuarios...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 relative">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-white">Panel de Administración</h2>
          <p className="text-sm text-gray-500 mt-0.5">Gestión de usuarios y sistema</p>
        </div>
        <div className="flex items-center gap-3">
          <div
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold"
            style={{ background: 'rgba(234,179,8,0.1)', border: '1px solid rgba(234,179,8,0.3)', color: '#ca8a04' }}
          >
            <AlertTriangle size={15} />
            Modo Administrador Activo
          </div>
          <button
            onClick={() => setShowNewUserModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white transition-opacity hover:opacity-90"
            style={{ background: '#2563eb' }}
          >
            <UserPlus size={15} />
            Registrar Usuario
          </button>
        </div>
      </div>

      {/* Users table */}
      <div
        className="rounded-2xl overflow-hidden mb-6"
        style={{ background: '#1a1a1e', border: '1px solid #2a2a2e' }}
      >
        <div
          className="grid text-xs font-semibold uppercase tracking-wider px-5 py-3"
          style={{ gridTemplateColumns: '1fr 180px 160px 1fr', color: '#555', borderBottom: '1px solid #2a2a2e' }}
        >
          <span>Nombre de Usuario</span>
          <span>Rol</span>
          <span>Carpetas</span>
          <span className="text-right">Acciones</span>
        </div>

        {users.map((user, i) => (
          <div
            key={user.id}
            className="grid items-center px-5 py-4 transition-colors hover:bg-white/2"
            style={{ gridTemplateColumns: '1fr 180px 160px 1fr', borderTop: i > 0 ? '1px solid #1e1e22' : undefined }}
          >
            <span className="text-white font-medium text-sm">{user.username}</span>

            {/* Selector de Rol */}
            <span>
              <select
                value={user.role}
                onChange={(e) => handleRoleChange(user.id, e.target.value as Role)}
                className="px-2.5 py-1 rounded-lg text-xs font-semibold outline-none cursor-pointer appearance-none text-center"
                style={{
                  background: user.role === 'admin' ? 'rgba(234,179,8,0.15)' : 'rgba(59,130,246,0.15)',
                  color: user.role === 'admin' ? '#ca8a04' : '#60a5fa',
                  border: '1px solid transparent'
                }}
              >
                <option value="user" className="bg-gray-900 text-white">Usuario</option>
                <option value="admin" className="bg-gray-900 text-white">Administrador</option>
              </select>
            </span>

            <span className="text-sm text-gray-400">{user.folders} carpetas</span>

            <div className="flex items-center justify-end gap-2">
              <button
                className="p-1.5 rounded-lg text-gray-500 hover:text-blue-400 hover:bg-blue-500/10 transition-colors"
                title="Gestionar temáticas"
              >
                <Folder size={15} />
              </button>
              <button
                onClick={() => setShowPassModal(user.id)}
                className="p-1.5 rounded-lg text-gray-500 hover:text-yellow-400 hover:bg-yellow-500/10 transition-colors"
                title="Cambiar contraseña"
              >
                <Key size={15} />
              </button>
              <button
                onClick={() => handleDeleteUser(user.id)}
                className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                title="Dar de baja"
              >
                <Trash2 size={15} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Admin power panel */}
      <div
        className="rounded-2xl p-5 flex items-start gap-4"
        style={{ background: '#1a1a1e', border: '1px solid #2a2a2e' }}
      >
        <AlertTriangle size={20} style={{ color: '#ca8a04' }} className="shrink-0 mt-0.5" />
        <div>
          <h4 className="text-white font-semibold flex items-center gap-2">
            <Shield size={15} style={{ color: '#ca8a04' }} />
            Poder de Administrador
          </h4>
          <p className="text-sm text-gray-500 mt-1 leading-relaxed">
            Como administrador, tienes control total sobre la plataforma. Cambiar roles u otorgar accesos de administrador a otros usuarios asi como eliminar usuarios, borrar y agregar categorias. debe hacerse con extrema precaución.
          </p>
        </div>
      </div>

      {/* ── Modales ── */}

      {showNewUserModal && (

        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl p-6" style={{ background: '#1c1c1e', border: '1px solid #2a2a2e' }}>
            <div className="flex justify-between items-center mb-5">
              <h3 className="text-lg font-semibold text-white">Registrar Usuario</h3>
              <button onClick={() => setShowNewUserModal(false)} className="text-gray-500 hover:text-white">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleCreateUser}>
              <label className="block text-sm text-gray-400 mb-1">Nombre de Usuario</label>
              <input type="text" value={newUsername} onChange={e => setNewUsername(e.target.value)} className="w-full mb-4 px-3 py-2 rounded-lg text-sm text-white outline-none" style={{ background: '#141416', border: '1px solid #2a2a2e' }} />
              
              <label className="block text-sm text-gray-400 mb-1">Contraseña</label>
              <input type="text" value={newPassword} onChange={e => setNewPassword(e.target.value)} className="w-full mb-4 px-3 py-2 rounded-lg text-sm text-white outline-none" style={{ background: '#141416', border: '1px solid #2a2a2e' }} />
              
              <label className="block text-sm text-gray-400 mb-1">Rol Inicial</label>
              <select value={newUserRole} onChange={e => setNewUserRole(e.target.value as Role)} className="w-full mb-6 px-3 py-2 rounded-lg text-sm text-white outline-none" style={{ background: '#141416', border: '1px solid #2a2a2e' }}>
                <option value="user">Usuario Estandar</option>
                <option value="admin">Administrador</option>
              </select>
              
              <button type="submit" className="w-full py-2.5 rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700">Crear Usuario</button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Cambiar Contraseña */}
      {showPassModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl p-6" style={{ background: '#1c1c1e', border: '1px solid #2a2a2e' }}>
            <div className="flex justify-between items-center mb-5">
              <h3 className="text-lg font-semibold text-white">Cambiar Contraseña</h3>
              <button onClick={() => setShowPassModal(null)} className="text-gray-500 hover:text-white">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleChangePassword}>
              <label className="block text-sm text-gray-400 mb-1">Nueva Contraseña</label>
              <input type="text" value={editPassword} onChange={e => setEditPassword(e.target.value)} className="w-full mb-6 px-3 py-2 rounded-lg text-sm text-white outline-none" style={{ background: '#141416', border: '1px solid #2a2a2e' }} placeholder="Ingresa la nueva contraseña porfaviurts" />
              
              <button type="submit"
              className="w-full py-2.5 rounded-lg font-semibold text-white text-sm transition-opacity hover:opacity-90"
              style={{ background: '#2563eb' }}>
                Actualizar Contraseña
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}