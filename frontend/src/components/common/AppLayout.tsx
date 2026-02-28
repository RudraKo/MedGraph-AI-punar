import { motion } from 'framer-motion'
import { Outlet, NavLink } from 'react-router-dom'
import { useSystemHealth } from '../../hooks/useSystemHealth'

const links = [
  { to: '/', label: 'Prescription Upload' },
  { to: '/dashboard', label: 'Risk Dashboard' },
]

export const AppLayout = () => {
  const { data } = useSystemHealth()
  const isReady = data?.status === 'ready'

  return (
    <div className="flex h-screen bg-surface-muted font-sans overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-surface-light border-r border-surface-border flex flex-col shadow-sm z-10">
        <div className="p-6 border-b border-surface-border">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-blue shadow-glow text-lg font-bold text-white">
              MG
            </div>
            <div>
              <p className="text-base font-bold tracking-tight text-brand-navy">MediGraph.AI</p>
              <p className="text-xs text-gray-500 font-medium">Clinical Safety</p>
            </div>
          </div>
        </div>

        <div className="px-4 py-6">
          <p className="px-2 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Patient Views</p>
          <nav className="flex flex-col gap-2">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-lg px-4 py-3 text-sm font-semibold transition-all ${isActive
                    ? 'bg-brand-blue/10 text-brand-blue'
                    : 'text-gray-600 hover:bg-gray-100/80 hover:text-gray-900'
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="mt-auto p-6 border-t border-surface-border">
          <div className="flex items-center gap-2 rounded-xl border border-surface-border bg-surface-muted px-4 py-3 text-sm font-medium text-gray-600">
            <span
              className={`h-2.5 w-2.5 rounded-full ${typeof isReady === 'undefined'
                  ? 'bg-gray-400 animate-pulse'
                  : isReady
                    ? 'bg-risk-safe'
                    : 'bg-risk-moderate'
                }`}
            />
            {typeof isReady === 'undefined' ? 'Checking Backend...' : isReady ? 'System Online' : 'Degraded'}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative h-full overflow-hidden">
        {/* Top Header */}
        <header className="h-20 bg-surface-light/80 backdrop-blur-md border-b border-surface-border flex items-center justify-between px-8 z-20">
          <h1 className="text-xl font-semibold text-brand-navy">Dashboard</h1>
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-full bg-brand-blue/10 border border-brand-blue/20 flex items-center justify-center text-brand-blue font-bold">
              DR
            </div>
          </div>
        </header>

        {/* Scrollable Content Container */}
        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-7xl px-8 py-8">
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
            >
              <Outlet />
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  )
}
