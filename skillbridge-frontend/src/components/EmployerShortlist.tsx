import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Search, Filter, CheckCircle2, XCircle, TrendingUp } from 'lucide-react'
import { motion } from 'framer-motion'
import { api } from '../lib/api'

const CANDIDATES = [
  { id: 101, name: 'Alice Chen', rank: 1, match: 94, matched: 8, missing: ['GraphQL'], recommendation: 'Highly recommended. Historical hires from this cluster retain > 90%.' },
  { id: 102, name: 'David Smith', rank: 2, match: 88, matched: 7, missing: ['Docker'], recommendation: 'Strong match on base requirements. Proficient in Python.' },
  { id: 103, name: 'Maria Garcia', rank: 3, match: 58, matched: 3, missing: ['Kubernetes', 'AWS'], recommendation: 'Shows high aptitude but lacks senior devops experience.' }
]

export default function EmployerShortlist() {
  const { jobId } = useParams()

  const handleHireAction = async (candidateId: number, outcome: string) => {
    try {
      await api.post(`/hire-outcomes`, { job_id: jobId, candidate_id: candidateId, outcome })
      // For demo we skip toast library
    } catch (err) {
      console.log(`Simulated ${outcome} recorded for Data Flywheel`)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in mt-4 pb-12">
      <Link to="/employer/jobs" className="inline-flex items-center gap-2 text-slate-500 hover:text-brand-600 transition-colors font-bold bg-white border border-slate-200 px-5 py-2.5 rounded-xl shadow-sm w-max">
        <ArrowLeft className="w-4 h-4" /> Back to Jobs
      </Link>

      <div>
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">AI Talent Shortlist</h1>
        <p className="text-slate-500 mt-2 font-bold text-lg">Ranking optimal candidates for <span className="text-brand-600">Senior AI Engineer</span></p>
      </div>

      {/* Flywheel Banner */}
      <motion.div initial={{ y: -10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-gradient-to-r from-brand-600 to-indigo-900 rounded-3xl p-6 text-white shadow-xl shadow-brand-500/20 flex flex-col sm:flex-row items-center justify-between border border-white/10 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
        <div className="flex items-center gap-5 relative z-10">
          <div className="bg-white/10 p-3.5 rounded-2xl backdrop-blur-md shadow-inner border border-white/20">
            <TrendingUp className="w-8 h-8 text-emerald-300" />
          </div>
          <div>
            <h3 className="font-black text-2xl leading-tight tracking-tight drop-shadow-md">Data Flywheel Active</h3>
            <p className="text-brand-100 text-sm font-medium mt-1">Every hire configuration decision actively retrains SkillBridge to source better matches globally.</p>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row justify-between items-center glass-panel p-4 gap-4">
        <div className="relative w-full md:w-96">
          <Search className="w-5 h-5 absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" />
          <input type="text" placeholder="Search parameters..." className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-4 focus:ring-brand-500/10 focus:border-brand-500 text-sm font-bold text-slate-700 bg-white shadow-inner transition-all" />
        </div>
        <div className="flex gap-4 w-full md:w-auto">
          <select className="px-5 py-3 rounded-xl border border-slate-200 outline-none text-sm font-bold text-slate-700 bg-white shadow-sm flex-1 md:flex-none">
            <option>Match &gt; 80%</option>
            <option>Match &gt; 60%</option>
          </select>
          <button className="btn-secondary py-3 px-6 flex items-center justify-center gap-2 text-sm font-bold flex-1 md:flex-none"><Filter className="w-4 h-4"/> Sort Config</button>
        </div>
      </div>

      {/* Candidate List */}
      <div className="space-y-5">
        {CANDIDATES.map((cand, index) => (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} key={cand.id} className="glass-card hover:border-brand-300 transition-all duration-300 p-6 sm:p-8 bg-white shadow-lg hover:shadow-xl group">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
              
              <div className="col-span-12 md:col-span-1 flex items-center justify-center md:border-r border-slate-100 pr-0 md:pr-4">
                <span className="text-5xl font-black text-slate-100 group-hover:text-brand-100 transition-colors">#{cand.rank}</span>
              </div>
              
              <div className="col-span-12 md:col-span-3">
                <h3 className="text-2xl font-black text-slate-800">{cand.name}</h3>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">ID: {cand.id}</p>
              </div>

              <div className="col-span-12 md:col-span-2">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-2xl font-black ${cand.match >= 80 ? 'text-emerald-500' : cand.match >= 60 ? 'text-amber-500' : 'text-rose-500'}`}>{cand.match}%</span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Match<br/>Index</span>
                </div>
                <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden shadow-inner">
                  <div className={`h-full ${cand.match >= 80 ? 'bg-emerald-500' : cand.match >= 60 ? 'bg-amber-500' : 'bg-rose-500'} transition-all duration-1000`} style={{ width: `${cand.match}%` }}></div>
                </div>
              </div>

              <div className="col-span-12 md:col-span-3 lg:pl-6">
                <p className="text-sm font-bold text-slate-500 mb-2"><span className="text-emerald-600 border border-emerald-200 bg-emerald-50 px-2 py-0.5 rounded-md mr-1">{cand.matched} Matched</span></p>
                <div className="flex gap-1.5 flex-wrap">
                  {cand.missing.map(m => <span key={m} className="badge-red py-[1px]">{m}</span>)}
                </div>
              </div>

              <div className="col-span-12 md:col-span-3 flex justify-start md:justify-end gap-3 mt-4 md:mt-0">
                <button className="btn-secondary text-sm px-6 font-bold shadow-sm">Review Profile</button>
                <button onClick={() => handleHireAction(cand.id, 'hired')} className="bg-emerald-50 border border-emerald-200 hover:bg-emerald-500 hover:text-white text-emerald-600 font-bold p-3 rounded-xl transition-all shadow-sm" title="Hire">
                  <CheckCircle2 className="w-5 h-5" />
                </button>
                <button onClick={() => handleHireAction(cand.id, 'rejected')} className="bg-rose-50 border border-rose-200 hover:bg-rose-500 hover:text-white text-rose-600 font-bold p-3 rounded-xl transition-all shadow-sm" title="Pass">
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              
            </div>
            
            <div className="mt-6 pt-5 border-t border-slate-100">
               <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-sm font-medium text-slate-600">
                 <strong className="text-slate-800">AI Note:</strong> {cand.recommendation}
               </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
