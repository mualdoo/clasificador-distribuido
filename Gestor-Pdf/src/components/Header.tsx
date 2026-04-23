import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, User, Shield, LogOut } from 'lucide-react';
import { Role } from '../types';

interface Props {
  username: string;
  role: Role;
  onRoleChange: (role: Role) => void;
  onLogout: () => void;
}

export default function Header({ username, role, onRoleChange, onLogout }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <header
      className="flex items-center justify-end px-5 py-2.5 border-b relative z-40"
      style={{ background: '#111113', borderColor: '#2a2a2e' }}
    >
      <div className="relative" ref={ref}>
        <button
          onClick={() => setOpen(v => !v)}
          className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg transition-colors hover:bg-white/5"
        >
          {/* Avatar */}
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
            style={{ background: '#2563eb' }}
          >
            {username[0]?.toUpperCase()}
          </div>
          <div className="text-left">
            <p className="text-sm font-medium text-white leading-tight">{username}</p>
            <p className="text-xs leading-tight" style={{ color: '#888' }}>
              {role === 'admin' ? 'Admin' : 'User'}
            </p>
          </div>
          <ChevronDown size={15} className="text-gray-400" />
        </button>

        {open && (
          <div
            className="absolute right-0 top-full mt-1 rounded-xl py-1.5 w-52 shadow-2xl z-50"
            style={{ background: '#1c1c1e', border: '1px solid #2a2a2e' }}
          >
            <p
              className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider"
              style={{ color: '#555' }}
            >
              Vista de Rol
            </p>

            <button
              onClick={() => { onRoleChange('user'); setOpen(false); }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-white/5"
              style={{ color: role === 'user' ? '#fff' : '#aaa' }}
            >
              <User size={15} />
              Usuario Estándar
              {role === 'user' && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500" />
              )}
            </button>

            <button
              onClick={() => { onRoleChange('admin'); setOpen(false); }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-white/5"
              style={{ color: role === 'admin' ? '#fff' : '#aaa' }}
            >
              <Shield size={15} />
              Administrador
              {role === 'admin' && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500" />
              )}
            </button>

            <div className="my-1.5" style={{ borderTop: '1px solid #2a2a2e' }} />

            <button
              onClick={() => { onLogout(); setOpen(false); }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-white/5 text-red-400"
            >
              <LogOut size={15} />
              Cerrar Sesión
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
