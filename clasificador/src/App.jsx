import { useState } from 'react'

const initialForm = {
  email: '',
  password: '',
  remember: false,
}

function App() {
  const [form, setForm] = useState(initialForm)
  const [showPassword, setShowPassword] = useState(false)
  const [status, setStatus] = useState({ type: 'idle', message: '' })

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target

    setForm((previousValue) => ({
      ...previousValue,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    if (!form.email.trim() || !form.password.trim()) {
      setStatus({
        type: 'error',
        message: 'Completa email y contrasena para continuar.',
      })
      return
    }

    setStatus({
      type: 'success',
      message: `Inicio de sesion simulado para ${form.email}.`,
    })

    setForm((previousValue) => ({
      ...previousValue,
      password: '',
    }))
  }

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-10 text-slate-100 sm:px-6 lg:px-8">
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -left-24 top-10 h-72 w-72 rounded-full bg-cyan-400/25 blur-3xl" />
        <div className="absolute right-0 top-1/3 h-80 w-80 rounded-full bg-fuchsia-400/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-60 w-60 rounded-full bg-emerald-300/15 blur-3xl" />
      </div>

      <section className="mx-auto grid w-full max-w-5xl overflow-hidden rounded-3xl border border-white/20 bg-white/10 shadow-2xl shadow-cyan-950/40 backdrop-blur-xl md:grid-cols-2">
        <aside className="hidden bg-gradient-to-br from-cyan-500/80 via-blue-600/80 to-indigo-700/90 p-10 md:flex md:flex-col md:justify-between">
          <div className="space-y-4">
            <p className="inline-flex rounded-full border border-white/35 bg-white/10 px-3 py-1 text-xs font-medium tracking-[0.2em] text-cyan-100">
              CLASIFICADOR DISTRIBUIDO
            </p>
            <h1 className="text-4xl font-semibold leading-tight text-white">
              Accede a tu panel
            </h1>
            <p className="text-sm leading-6 text-cyan-100/90">
              Inicia sesion para administrar nodos, revisar tareas pendientes y
              ver el estado del sistema en tiempo real.
            </p>
          </div>

          <ul className="space-y-3 text-sm text-cyan-100/95">
            <li>Monitoreo de nodos en tiempo real</li>
            <li>Sincronizacion centralizada de datos</li>
            <li>Alertas de procesos criticos</li>
          </ul>
        </aside>

        <div className="bg-slate-950/55 p-6 sm:p-10">
          <div className="mb-8 space-y-2">
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-cyan-200">
              Bienvenido
            </p>
            <h2 className="text-3xl font-semibold text-white">Iniciar sesion</h2>
            <p className="text-sm text-slate-300">
              Ingresa tus credenciales para continuar.
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <label className="block space-y-2">
              <span className="text-sm text-slate-200">Email</span>
              <input
                className="w-full rounded-xl border border-white/20 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-400 focus:border-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-300/30"
                name="email"
                type="email"
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                placeholder="admin@empresa.com"
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm text-slate-200">Contrasena</span>
              <div className="relative">
                <input
                  className="w-full rounded-xl border border-white/20 bg-slate-900/80 px-4 py-3 pr-24 text-sm text-slate-100 placeholder:text-slate-400 focus:border-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-300/30"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="********"
                />
                <button
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md px-2 py-1 text-xs font-medium text-cyan-200 transition hover:bg-cyan-200/15"
                  type="button"
                  onClick={() => setShowPassword((previousValue) => !previousValue)}
                >
                  {showPassword ? 'Ocultar' : 'Mostrar'}
                </button>
              </div>
            </label>

            <div className="flex items-center justify-between gap-3 text-sm">
              <label className="inline-flex items-center gap-2 text-slate-300">
                <input
                  className="h-4 w-4 rounded border-white/20 bg-slate-900 text-cyan-300 focus:ring-cyan-300"
                  name="remember"
                  type="checkbox"
                  checked={form.remember}
                  onChange={handleChange}
                />
                Recordarme
              </label>
              <a className="text-cyan-200 transition hover:text-cyan-100" href="#">
                Olvide mi contrasena
              </a>
            </div>

            <button
              className="w-full rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-105 focus:outline-none focus:ring-2 focus:ring-cyan-300/50"
              type="submit"
            >
              Entrar
            </button>
          </form>

          {status.message ? (
            <p
              className={`mt-5 rounded-lg border px-4 py-3 text-sm ${
                status.type === 'error'
                  ? 'border-rose-300/40 bg-rose-400/10 text-rose-200'
                  : 'border-emerald-300/40 bg-emerald-400/10 text-emerald-200'
              }`}
              role="status"
            >
              {status.message}
            </p>
          ) : null}

          <p className="mt-6 text-xs text-slate-400">
            Demo local sin backend. Puedes conectar este formulario a tu API de
            autenticacion cuando quieras.
          </p>
        </div>
      </section>
    </main>
  )
}

export default App
