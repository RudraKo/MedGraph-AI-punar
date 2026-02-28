import { NavLink } from 'react-router-dom'

import { useSystemHealth } from '../../hooks/useSystemHealth'

const links = [
  { to: '/', label: 'Prescription Upload' },
  { to: '/dashboard', label: 'Risk Dashboard' },
]

export const Navbar = () => {
  const { data } = useSystemHealth()
  const isReady = data?.status === 'ready'

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/85 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-clinic-600 text-sm font-bold text-white">
            MG
          </div>
          <div>
            <p className="text-sm font-bold tracking-tight text-slate-900">MediGraph.AI</p>
            <p className="text-xs text-slate-500">Clinical Safety Intelligence</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 sm:flex">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                typeof isReady === 'undefined'
                  ? 'bg-slate-400'
                  : isReady
                    ? 'bg-emerald-500'
                    : 'bg-amber-500'
              }`}
            />
            {typeof isReady === 'undefined' ? 'Checking backend' : isReady ? 'Backend Ready' : 'Degraded'}
          </div>

          <nav className="flex items-center gap-1 rounded-xl border border-slate-200 bg-white p-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-xs font-semibold transition sm:text-sm ${
                  isActive ? 'bg-clinic-600 text-white' : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          </nav>
        </div>
      </div>
    </header>
  )
}
