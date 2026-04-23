import React, { useState } from 'react';
import { X } from 'lucide-react';

interface Props {
  onLogin: (username: string, role: 'admin' | 'user') => void;
}

export default function LoginModal({ onLogin }: Props) {
  const [tab, setTab] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [regUser, setRegUser] = useState('');
  const [regPass, setRegPass] = useState('');
  const [regPass2, setRegPass2] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!username || !password) {
      setError('Por favor completa todos los campos.');
      return;
    }
    if (username === 'admin' && password === 'admin') {
      onLogin('admin', 'admin');
    } else {
      onLogin(username, 'user');
    }
  };

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!regUser || !regPass || !regPass2) {
      setError('Por favor completa todos los campos.');
      return;
    }
    if (regPass !== regPass2) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    onLogin(regUser, 'user');
  };

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
      <div
        className="rounded-xl p-7 w-full max-w-sm relative"
        style={{ background: '#1c1c1e', border: '1px solid #2a2a2e' }}
      >
        {/* Title */}
        <h2 className="text-white text-xl font-semibold mb-5">Gestor PDF</h2>

        {/* Tabs */}
        <div
          className="flex rounded-full mb-6 p-1"
          style={{ background: '#2a2a2e' }}
        >
          <button
            onClick={() => { setTab('login'); setError(''); }}
            className="flex-1 py-1.5 rounded-full text-sm font-medium transition-all"
            style={{
              background: tab === 'login' ? '#3a3a3e' : 'transparent',
              color: tab === 'login' ? '#fff' : '#888',
            }}
          >
            Iniciar Sesión
          </button>
          <button
            onClick={() => { setTab('register'); setError(''); }}
            className="flex-1 py-1.5 rounded-full text-sm font-medium transition-all"
            style={{
              background: tab === 'register' ? '#3a3a3e' : 'transparent',
              color: tab === 'register' ? '#fff' : '#888',
            }}
          >
            Registrarse
          </button>
        </div>

        {/* Login Form */}
        {tab === 'login' && (
          <form onSubmit={handleLogin}>
            <label className="block text-sm text-gray-300 mb-1">Usuario</label>
            <input
              type="text"
              placeholder="Ingrese su usuario"
              value={username}
              onChange={e => setUsername(e.target.value)}
              className="w-full mb-4 px-3 py-2.5 rounded-lg text-sm text-white placeholder-gray-500 outline-none"
              style={{ background: '#2a2a2e', border: '1px solid #3a3a3e' }}
            />
            <label className="block text-sm text-gray-300 mb-1">Contraseña</label>
            <input
              type="password"
              placeholder="Ingrese su contraseña"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full mb-3 px-3 py-2.5 rounded-lg text-sm text-white placeholder-gray-500 outline-none"
              style={{ background: '#2a2a2e', border: '1px solid #3a3a3e' }}
            />
            <p className="text-xs text-gray-500 mb-4">
              La contraseña y usuario actual de Administrador es "admin" UWU
            </p>
            {error && <p className="text-red-400 text-xs mb-3">{error}</p>}
            <button
              type="submit"
              className="w-full py-2.5 rounded-lg font-semibold text-white text-sm transition-opacity hover:opacity-90"
              style={{ background: '#2563eb' }}
            >
              Iniciar Sesión
            </button>
          </form>
        )}

        {/* Register Form */}
        {tab === 'register' && (
          <form onSubmit={handleRegister}>
            <label className="block text-sm text-gray-300 mb-1">Usuario</label>
            <input
              type="text"
              placeholder="Elige un nombre de usuario"
              value={regUser}
              onChange={e => setRegUser(e.target.value)}
              className="w-full mb-4 px-3 py-2.5 rounded-lg text-sm text-white placeholder-gray-500 outline-none"
              style={{ background: '#2a2a2e', border: '1px solid #3a3a3e' }}
            />
            <label className="block text-sm text-gray-300 mb-1">Contraseña</label>
            <input
              type="password"
              placeholder="Crea una contraseña"
              value={regPass}
              onChange={e => setRegPass(e.target.value)}
              className="w-full mb-4 px-3 py-2.5 rounded-lg text-sm text-white placeholder-gray-500 outline-none"
              style={{ background: '#2a2a2e', border: '1px solid #3a3a3e' }}
            />
            <label className="block text-sm text-gray-300 mb-1">Confirmar contraseña</label>
            <input
              type="password"
              placeholder="Repite la contraseña"
              value={regPass2}
              onChange={e => setRegPass2(e.target.value)}
              className="w-full mb-4 px-3 py-2.5 rounded-lg text-sm text-white placeholder-gray-500 outline-none"
              style={{ background: '#2a2a2e', border: '1px solid #3a3a3e' }}
            />
            {error && <p className="text-red-400 text-xs mb-3">{error}</p>}
            <button
              type="submit"
              className="w-full py-2.5 rounded-lg font-semibold text-white text-sm transition-opacity hover:opacity-90"
              style={{ background: '#2563eb' }}
            >
              Crear Cuenta
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
