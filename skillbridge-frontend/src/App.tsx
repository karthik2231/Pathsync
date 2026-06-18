import { Outlet, Link } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { BrainCircuit, LogOut, User } from 'lucide-react'

function App() {
  const { role, logout } = useAuthStore()
  
  // Set mock candidate by default for demo purposes if nothing set
  if (!role) {
      useAuthStore.getState().setAuth('mock_token', 'candidate', 1)
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <nav className="glass-panel sticky top-0 z-50 flex justify-between items-center px-6 py-4 mx-4 mt-4 mb-2">
        <Link to="/" className="flex items-center gap-3">
          <div className="bg-brand-600 p-2 rounded-xl shadow-md border border-brand-500">
            <BrainCircuit className="text-white w-6 h-6" />
          </div>
          <span className="text-2xl font-bold bg-gradient-to-br from-brand-700 to-brand-400 bg-clip-text text-transparent transform md:translate-y-px">
            SkillBridge
          </span>
        </Link>
        
        <div className="flex items-center gap-6">
          <div className="hidden md:flex gap-6 items-center">
              {role === 'candidate' && (
                <Link to="/dashboard" className="text-slate-600 hover:text-brand-600 font-medium transition-colors">Dashboard</Link>
              )}
              {role === 'employer' && (
                <>
                  <Link to="/employer/post-job" className="text-slate-600 hover:text-brand-600 font-medium transition-colors">Post Job</Link>
                  <Link to="/employer/jobs" className="text-slate-600 hover:text-brand-600 font-medium transition-colors">My Jobs</Link>
                </>
              )}
          </div>
          
          <div className="h-8 w-px bg-slate-200 mx-2 hidden md:block"></div>
          
          <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-slate-100 rounded-full pr-4 pl-1 py-1 border border-slate-200">
                  <div className="bg-white p-1 rounded-full shadow-sm">
                      <User className="w-4 h-4 text-slate-500" />
                  </div>
                  <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider">{role}</span>
              </div>
              <button onClick={logout} className="flex items-center gap-2 text-slate-400 hover:text-rose-500 transition-colors">
                <LogOut className="w-5 h-5" />
              </button>
          </div>
        </div>
      </nav>

      {/* Background ambient blurring */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 bg-slate-50 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-brand-200/40 blur-3xl animate-blob"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-blue-200/30 blur-3xl animate-blob" style={{ animationDelay: '2s' }}></div>
      </div>

      <main className="flex-1 w-full max-w-7xl mx-auto p-4 md:p-8 relative z-10 animate-fade-in">
        <Outlet />
      </main>
    </div>
  )
}

export default App
