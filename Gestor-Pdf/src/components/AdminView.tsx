import React from 'react';
import { Folder, Key, Trash2, AlertTriangle, Shield } from 'lucide-react';
import { User } from '../types';

interface Props {
  users: User[];
  onDeleteUser: (id: string) => void;
}

export default function AdminView({ users, onDeleteUser }: Props) {
  return (
    <div className="flex-1 overflow-y-auto p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-white">Panel de Administración</h2>
          <p className="text-sm text-gray-500 mt-0.5">Gestión de usuarios y sistema</p>
        </div>
        <div
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold"
          style={{ background: 'rgba(234,179,8,0.1)', border: '1px solid rgba(234,179,8,0.3)', color: '#ca8a04' }}
        >
          <AlertTriangle size={15} />
          Modo Administrador Activo
        </div>
      </div>

      {/* Users table */}
      <div
        className="rounded-2xl overflow-hidden mb-6"
        style={{ background: '#1a1a1e', border: '1px solid #2a2a2e' }}
      >
        {/* Table header */}
        <div
          className="grid text-xs font-semibold uppercase tracking-wider px-5 py-3"
          style={{
            gridTemplateColumns: '1fr 180px 160px 1fr',
            color: '#555',
            borderBottom: '1px solid #2a2a2e'
          }}
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
            style={{
              gridTemplateColumns: '1fr 180px 160px 1fr',
              borderTop: i > 0 ? '1px solid #1e1e22' : undefined,
            }}
          >
            <span className="text-white font-medium text-sm">{user.username}</span>

            <span>
              <span
                className="px-2.5 py-0.5 rounded-full text-xs font-semibold"
                style={{
                  background: user.role === 'admin' ? 'rgba(234,179,8,0.15)' : 'rgba(59,130,246,0.15)',
                  color: user.role === 'admin' ? '#ca8a04' : '#60a5fa',
                }}
              >
                {user.role === 'admin' ? 'Administrador' : 'Usuario'}
              </span>
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
                className="p-1.5 rounded-lg text-gray-500 hover:text-yellow-400 hover:bg-yellow-500/10 transition-colors"
                title="Cambiar contraseña"
              >
                <Key size={15} />
              </button>
              <button
                onClick={() => onDeleteUser(user.id)}
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
            Como administrador, puedes eliminar cualquier carpeta de cualquier usuario, incluso si contiene archivos.
            Esta acción es irreversible y debe usarse con precaución.
          </p>
        </div>
      </div>
    </div>
  );
}
