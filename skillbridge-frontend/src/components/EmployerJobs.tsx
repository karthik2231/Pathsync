import { Link, useNavigate } from 'react-router-dom'
import { Users, Filter, Search, ArrowRightCircle } from 'lucide-react'

const MOCK_JOBS = [
  { id: 1, title: 'Senior AI Engineer', status: 'active', applicants: 124, matchRate: 88, posted: '2 days ago' },
  { id: 2, title: 'Full Stack Developer', status: 'active', applicants: 89, matchRate: 72, posted: '5 days ago' },
  { id: 3, title: 'Data Scientist', status: 'closed', applicants: 210, matchRate: 91, posted: '12 days ago' },
]

export default function EmployerJobs() {
  const navigate = useNavigate()

  return (
    <div className="space-y-8 animate-fade-in mt-6">
      <div className="flex justify-between items-end mb-10">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Active Pipelines</h1>
          <p className="text-lg text-slate-500 mt-2 font-medium">Manage active roles and pipeline performance.</p>
        </div>
        <Link to="/employer/post-job" className="btn-primary text-lg px-8 py-3 shadow-brand-500/30">
          + New Job Positing
        </Link>
      </div>

      <div className="glass-panel overflow-hidden shadow-xl border-white/60">
        <div className="flex flex-col sm:flex-row justify-between items-center p-5 bg-white border-b border-slate-100 gap-4">
          <div className="relative w-full sm:w-80">
            <Search className="w-5 h-5 absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-300" />
            <input type="text" placeholder="Search roles..." className="w-full pl-12 pr-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-4 focus:ring-brand-500/10 focus:border-brand-500 text-sm font-bold text-slate-700 transition-all shadow-inner" />
          </div>
          <button className="btn-secondary font-bold flex items-center gap-2 py-3 px-6 shadow-sm border-slate-200 w-full sm:w-auto justify-center">
            <Filter className="w-4 h-4" /> Filters
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr className="bg-slate-50/50">
                <th className="py-5 px-8 text-xs font-black text-slate-400 uppercase tracking-widest border-b border-slate-200">Role Title</th>
                <th className="py-5 px-8 text-xs font-black text-slate-400 uppercase tracking-widest text-center border-b border-slate-200">Status</th>
                <th className="py-5 px-8 text-xs font-black text-slate-400 uppercase tracking-widest text-center border-b border-slate-200">Top Matches</th>
                <th className="py-5 px-8 text-xs font-black text-slate-400 uppercase tracking-widest text-center border-b border-slate-200">Avg Confidence</th>
                <th className="py-5 px-8 text-xs font-black text-slate-400 uppercase tracking-widest text-right border-b border-slate-200">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {MOCK_JOBS.map(job => (
                <tr key={job.id} onClick={() => navigate(`/employer/jobs/${job.id}/candidates`)} className="hover:bg-brand-50/30 transition-all cursor-pointer group">
                  <td className="py-6 px-8">
                    <span className="font-black text-slate-800 text-xl group-hover:text-brand-600 transition-colors drop-shadow-sm">{job.title}</span>
                    <div className="text-xs text-slate-400 font-bold mt-2 tracking-wide uppercase">Posted {job.posted}</div>
                  </td>
                  <td className="py-6 px-8 text-center">
                    <span className={`px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest ${job.status === 'active' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-sm' : 'bg-slate-100 text-slate-500 border border-slate-200 shadow-sm'}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="py-6 px-8 text-center">
                    <div className="flex items-center justify-center gap-2 text-slate-700 font-black text-lg">
                      <Users className="w-5 h-5 text-slate-300" /> {job.applicants}
                    </div>
                  </td>
                  <td className="py-6 px-8 text-center">
                    <span className={`font-black text-2xl drop-shadow-sm ${job.matchRate > 85 ? 'text-emerald-500' : 'text-amber-500'}`}>{job.matchRate}%</span>
                  </td>
                  <td className="py-6 px-8 text-right">
                    <button className="p-3 text-brand-400 group-hover:bg-brand-500 group-hover:text-white rounded-xl transition-all shadow-sm border border-transparent group-hover:border-brand-600">
                      <ArrowRightCircle className="w-6 h-6" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
