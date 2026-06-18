import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, ChevronDown, ChevronUp, BookOpen, AlertTriangle, AlertCircle, PlayCircle, Info } from 'lucide-react'

// Mock Data
const REPORT = {
  score: 82,
  title: "Full Stack Developer",
  company: "CloudBase",
  hard_gaps: ["AWS", "Docker"],
  soft_gaps: ["GraphQL"],
  proficiency_gaps: [
    { skill: "React", have: 3, need: 4 },
    { skill: "Node.js", have: 2, need: 3 }
  ],
  learning_path: [
    { id: 1, title: "AWS Solutions Architect Crash Course", hours: 12, platform: "Coursera" },
    { id: 2, title: "Docker Mastery", hours: 8, platform: "Udemy" }
  ]
}

export default function GapReport() {
  const { jobId } = useParams()
  const [showExplanation, setShowExplanation] = useState(false)

  // Circle animation variables for Speedometer
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (REPORT.score / 100) * circumference;

  return (
    <div className="max-w-5xl mx-auto pb-16 animate-fade-in lg:mt-6">
      <Link to="/dashboard" className="inline-flex items-center gap-2 text-slate-500 hover:text-brand-600 transition-colors mb-8 font-semibold bg-white px-4 py-2 rounded-lg shadow-sm w-max">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      <div className="glass-panel p-8 md:p-10 mb-8 relative overflow-hidden shadow-xl border-white/60">
        <div className="absolute top-[-50%] right-[-10%] w-[400px] h-[400px] bg-brand-200 rounded-full blur-3xl opacity-30 pointer-events-none animate-pulse-slow"></div>

        <div className="flex flex-col md:flex-row items-center gap-12 relative z-10">
          <div className="relative w-48 h-48 flex-shrink-0 drop-shadow-xl bg-white rounded-full p-2">
            <svg className="w-full h-full transform -rotate-90 drop-shadow-md">
              <circle cx="88" cy="88" r="40" stroke="#f1f5f9" strokeWidth="12" fill="none" />
              <motion.circle 
                cx="88" cy="88" r="40" 
                stroke={REPORT.score >= 80 ? '#10b981' : '#f59e0b'} 
                strokeWidth="12" 
                fill="none" 
                strokeLinecap="round"
                initial={{ strokeDasharray: circumference, strokeDashoffset: circumference }}
                animate={{ strokeDashoffset }}
                transition={{ duration: 1.5, ease: "easeOut", type: "spring" }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-5xl font-black text-slate-800 tracking-tighter">{REPORT.score}<span className="text-2xl text-slate-300">%</span></span>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-widest mt-1">Match Confidence</span>
            </div>
          </div>

          <div className="text-center md:text-left">
            <div className="inline-block bg-slate-100 text-slate-500 px-3 py-1 rounded-full text-xs font-bold mb-3 uppercase tracking-wider">{REPORT.company}</div>
            <h1 className="text-4xl font-black text-slate-900 mb-3 tracking-tight">{REPORT.title}</h1>
            <p className="text-lg text-slate-600 mb-6 font-medium leading-relaxed max-w-xl">You match {REPORT.score}% of this role. You possess <span className="text-emerald-600 font-bold">6 critical required skills</span>, but are missing key infra knowledge.</p>
            
            <button className="btn-primary text-lg px-8 py-3 shadow-brand-500/40">Apply Now on System</button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6 border-l-4 border-l-rose-500 shadow-md">
            <h3 className="text-lg font-bold flex items-center gap-2 text-rose-700 mb-4">
              <AlertCircle className="w-5 h-5"/> Hard Gaps (Required)
            </h3>
            <div className="flex gap-3 flex-wrap">
              {REPORT.hard_gaps.map(g => <span key={g} className="badge-red text-sm px-4 py-1.5 shadow-sm">{g}</span>)}
            </div>
          </div>

          <div className="glass-card p-6 border-l-4 border-l-amber-500 shadow-md">
            <h3 className="text-lg font-bold flex items-center gap-2 text-amber-700 mb-4">
              <AlertTriangle className="w-5 h-5"/> Soft Gaps (Preferred)
            </h3>
            <div className="flex gap-3 flex-wrap">
              {REPORT.soft_gaps.map(g => <span key={g} className="badge-amber text-sm px-4 py-1.5 shadow-sm">{g}</span>)}
            </div>
          </div>

          <div className="glass-card p-6 shadow-md overflow-hidden">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Proficiency Improvements Needed</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/50">
                    <th className="py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-widest rounded-l-lg">Skill Target</th>
                    <th className="py-3 px-4 text-xs font-bold text-slate-400 uppercase tracking-widest text-center">Your Level</th>
                    <th className="py-3 px-4 text-xs font-bold text-brand-500 uppercase tracking-widest text-center rounded-r-lg">Benchmark</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {REPORT.proficiency_gaps.map((p, i) => (
                    <tr key={i} className="hover:bg-slate-50/50 transition-colors">
                      <td className="py-4 px-4 font-bold text-slate-700">{p.skill}</td>
                      <td className="py-4 px-4 text-center">
                        <span className="bg-slate-100 text-slate-600 px-3 py-1.5 rounded-lg font-semibold border border-slate-200">{p.have}/5</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="bg-brand-50 text-brand-600 px-3 py-1.5 rounded-lg font-bold border border-brand-100">{p.need}/5</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card p-6 bg-gradient-to-br from-brand-700 to-indigo-900 text-white border-none shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-2xl"></div>
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 relative z-10">
              <BookOpen className="w-5 h-5"/> Curated Path
            </h3>
            <div className="space-y-4 relative z-10">
              {REPORT.learning_path.map(course => (
                <div key={course.id} className="bg-white/10 hover:bg-white/20 border border-white/10 transition-colors p-5 rounded-2xl cursor-pointer shadow-lg backdrop-blur-sm">
                  <h4 className="font-bold mb-3 leading-snug">{course.title}</h4>
                  <div className="flex justify-between items-center text-xs font-bold text-brand-200 uppercase tracking-wider">
                    <span>{course.platform}</span>
                    <span className="flex items-center gap-1.5 bg-black/20 px-2 py-1 rounded-md"><PlayCircle className="w-4 h-4 text-emerald-400"/> {course.hours} hrs</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="glass-panel rounded-2xl border border-slate-200 bg-white">
            <button 
              onClick={() => setShowExplanation(!showExplanation)}
              className="w-full flex justify-between items-center p-5 font-bold text-slate-700 hover:bg-slate-50 rounded-2xl transition-colors"
            >
              <div className="flex items-center gap-2"><Info className="w-4 h-4 text-brand-500"/> Methodology</div>
              {showExplanation ? <ChevronUp className="w-4 h-4 text-slate-400"/> : <ChevronDown className="w-4 h-4 text-slate-400"/>}
            </button>
            {showExplanation && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                className="p-5 pt-0 text-sm font-medium text-slate-500 space-y-3 leading-relaxed"
              >
                <p>Calculations map your parsed resume vs the job listing using <strong>Sentence-Transformer Embeddings (all-MiniLM-L6)</strong> and ESCO ontology.</p>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <p className="text-slate-700"><span className="font-bold text-brand-600">Hard Required:</span> 70% weight</p>
                  <p className="text-slate-700"><span className="font-bold text-amber-500">Soft Preferred:</span> 30% weight</p>
                  <p className="text-slate-700 mt-2 text-xs">-3 points penalty per missing proficiency tier.</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
