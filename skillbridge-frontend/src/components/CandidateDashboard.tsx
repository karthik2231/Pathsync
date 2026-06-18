import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { Briefcase, ArrowRight, CheckCircle2, XCircle, ExternalLink } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

// Mock Data because we don't have a populated live DB attached immediately
const MOCK_RADAR_DATA = [
  { subject: 'Python', A: 90, B: 85, fullMark: 100 },
  { subject: 'React', A: 85, B: 90, fullMark: 100 },
  { subject: 'Docker', A: 40, B: 80, fullMark: 100 },
  { subject: 'AWS', A: 50, B: 75, fullMark: 100 },
  { subject: 'System Design', A: 70, B: 85, fullMark: 100 },
  { subject: 'Data Structures', A: 85, B: 85, fullMark: 100 },
]

const MOCK_JOBS = [
  { id: 1, title: 'Senior AI Engineer', company: 'TechNova', match: 94, missing: ['Docker', 'Kubernetes'] },
  { id: 2, title: 'Full Stack Developer', company: 'CloudBase', match: 88, missing: ['AWS'] },
  { id: 3, title: 'Backend Software Engineer', company: 'DataFlow', match: 81, missing: ['Go', 'Redis'] },
]

const MOCK_GAPS = {
  have: ['Python', 'React', 'TypeScript', 'Node.js', 'PostgreSQL'],
  missing: [
    { skill: 'Docker', courseUrl: 'https://udemy.com/docker-mastery' },
    { skill: 'AWS', courseUrl: 'https://aws.amazon.com/training/' },
    { skill: 'Kubernetes', courseUrl: 'https://kubernetes.io/training/' }
  ]
}

export default function CandidateDashboard() {
  const { userId } = useAuthStore()

  return (
    <div className="space-y-8 animate-fade-in">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, John</h1>
        <p className="text-slate-500 mt-1">Here is your AI-powered career analysis.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Radar Chart */}
        <div className="glass-panel p-6 col-span-1 lg:col-span-2 shadow-lg hover:shadow-xl transition-shadow">
          <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-3">
            Skill Analysis 
            <span className="text-xs font-semibold text-brand-700 bg-brand-50 px-3 py-1 rounded-full border border-brand-100">vs Target Role Avg</span>
          </h2>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={MOCK_RADAR_DATA}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 13, fontWeight: 500 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}/>
                <Radar name="You" dataKey="A" stroke="#4f46e5" fill="#6366f1" fillOpacity={0.4} strokeWidth={3} />
                <Radar name="Market Avg" dataKey="B" stroke="#94a3b8" fill="#cbd5e1" fillOpacity={0.2} strokeDasharray="4 4" strokeWidth={2}/>
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Skill Gap Panel */}
        <div className="glass-panel p-6 flex flex-col shadow-lg">
          <h2 className="text-xl font-bold text-slate-800 mb-6">Your Profile Snapshot</h2>
          
          <div className="mb-8">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500"/> You Have
            </h3>
            <div className="flex flex-wrap gap-2">
              {MOCK_GAPS.have.map(s => (
                <span key={s} className="badge-green">{s}</span>
              ))}
            </div>
          </div>

          <div className="flex-1">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-500"/> Critical Gaps
            </h3>
            <div className="space-y-3">
              {MOCK_GAPS.missing.map(m => (
                <div key={m.skill} className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white hover:border-brand-300 transition-colors shadow-sm">
                  <span className="font-semibold text-slate-700">{m.skill}</span>
                  <a href={m.courseUrl} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-xs font-bold text-brand-600 hover:text-white hover:bg-brand-500 bg-brand-50 px-3 py-1.5 rounded-lg transition-all">
                    Learn <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Top Job Matches */}
      <div className="mt-10">
        <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
           Highest Probability Matches <span className="text-sm font-normal text-slate-500 ml-2">Based on Vector Embeddings</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {MOCK_JOBS.map(job => (
            <div key={job.id} className="glass-card p-6 flex flex-col bg-white hover:scale-[1.02] hover:shadow-xl transition-all duration-300 cursor-pointer border-transparent hover:border-brand-200">
              <div className="flex justify-between items-start mb-5">
                <div className="flex gap-4 items-center">
                  <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center border border-slate-200 shadow-inner">
                    <Briefcase className="w-6 h-6 text-brand-500" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 leading-tight text-lg">{job.title}</h3>
                    <p className="text-sm font-medium text-slate-500">{job.company}</p>
                  </div>
                </div>
                <div className="flex flex-col items-center bg-brand-50 px-3 py-2 rounded-xl border border-brand-100">
                  <span className={`text-xl font-black ${job.match >= 90 ? 'text-emerald-600' : 'text-brand-600'}`}>
                    {job.match}%
                  </span>
                </div>
              </div>
              
              <div className="mt-auto pt-5 border-t border-slate-100">
                <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Lacking Skills</p>
                <div className="flex flex-wrap gap-2 mb-6 min-h-[28px]">
                  {job.missing.map(m => (
                    <span key={m} className="badge-red px-2 py-0.5">{m}</span>
                  ))}
                </div>
                
                <Link to={`/jobs/${job.id}/gap-report`} className="btn-primary w-full flex justify-center items-center gap-2 py-3">
                  Analyze Gap <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
