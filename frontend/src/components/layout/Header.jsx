import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import NotificationBell from '../ui/NotificationBell'

function NavItem({ to, onClick, children }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        `block px-4 py-2.5 text-sm font-medium rounded-xl transition-colors
         ${isActive
           ? 'bg-primary-50 text-primary-600'
           : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`
      }
    >
      {children}
    </NavLink>
  )
}

export function Header() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const close = () => setMenuOpen(false)

  const handleLogout = async () => {
    close()
    await logout()
    navigate('/login')
  }

  const isSeller = user?.role === 'seller' || user?.role === 'builder'
  const isAdvocate = user?.role === 'advocate'

  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" onClick={close} className="text-primary-500 font-bold text-lg shrink-0">
          Property Connect
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {isAuthenticated ? (
            <>
              <NavItem to="/properties">Browse</NavItem>
              {isSeller   && <NavItem to="/my-listings">My Listings</NavItem>}
              {isAdvocate && <NavItem to="/verifications">Verifications</NavItem>}
              <NavItem to="/pricing">Pricing</NavItem>
              <NavItem to="/chat">Messages</NavItem>
              <NotificationBell />
              <span className="text-sm text-gray-500 px-2">{user?.first_name}</span>
              <button
                onClick={handleLogout}
                className="ml-1 px-3 py-1.5 text-sm font-medium border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 transition-colors"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-4 py-1.5 text-sm font-medium border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 transition-colors">
                Sign In
              </Link>
              <Link to="/register" className="px-4 py-1.5 text-sm font-semibold bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors">
                Register
              </Link>
            </>
          )}
        </nav>

        {/* Mobile right side */}
        <div className="flex md:hidden items-center gap-2">
          {isAuthenticated && <NotificationBell />}
          <button
            aria-label="Toggle menu"
            onClick={() => setMenuOpen((o) => !o)}
            className="p-2 rounded-xl text-gray-600 hover:bg-gray-100 transition-colors"
          >
            {menuOpen ? (
              /* X icon */
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              /* Hamburger icon */
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 px-4 py-3 flex flex-col gap-1 shadow-lg">
          {isAuthenticated ? (
            <>
              <div className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                {user?.first_name} · {user?.role}
              </div>
              <NavItem to="/properties" onClick={close}>Browse Properties</NavItem>
              {isSeller   && <NavItem to="/my-listings" onClick={close}>My Listings</NavItem>}
              {isAdvocate && <NavItem to="/verifications" onClick={close}>Verifications</NavItem>}
              <NavItem to="/chat" onClick={close}>Messages</NavItem>
              <NavItem to="/notifications" onClick={close}>Notifications</NavItem>
              <NavItem to="/pricing" onClick={close}>Pricing</NavItem>
              <div className="border-t border-gray-100 mt-2 pt-2">
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2.5 text-sm font-medium text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <NavItem to="/properties" onClick={close}>Browse Properties</NavItem>
              <NavItem to="/pricing" onClick={close}>Pricing</NavItem>
              <div className="border-t border-gray-100 mt-2 pt-2 flex flex-col gap-2">
                <Link
                  to="/login"
                  onClick={close}
                  className="block text-center px-4 py-2.5 text-sm font-medium border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={close}
                  className="block text-center px-4 py-2.5 text-sm font-semibold bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors"
                >
                  Register
                </Link>
              </div>
            </>
          )}
        </div>
      )}
    </header>
  )
}
