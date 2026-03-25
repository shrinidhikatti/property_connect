import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

function Tab({ to, label, icon }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex flex-col items-center gap-0.5 px-3 py-2 text-xs font-medium transition-colors
         ${isActive ? 'text-primary-500' : 'text-gray-400'}`
      }
    >
      <span className="text-xl leading-none">{icon}</span>
      {label}
    </NavLink>
  )
}

export function BottomNav() {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return null

  const isSeller  = user?.role === 'seller' || user?.role === 'builder'
  const isAdvocate = user?.role === 'advocate'

  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white border-t border-gray-200 flex justify-around safe-area-pb">
      <Tab to="/properties"   label="Browse"    icon="🏠" />
      {isSeller   && <Tab to="/my-listings"  label="Listings"  icon="📋" />}
      {isAdvocate && <Tab to="/verifications" label="Reviews"  icon="✅" />}
      <Tab to="/chat"         label="Messages"  icon="💬" />
      <Tab to="/pricing"      label="Plans"     icon="⭐" />
    </nav>
  )
}
