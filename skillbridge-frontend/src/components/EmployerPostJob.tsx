import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, DollarSign, Check, X, PlusCircle, ArrowRight, ArrowLeft } from 'lucide-react'
import { api } from '../lib/api'

export default function EmployerPostJob() {
  const [step, setStep] = useState(1)
  const navigate = useNavigate()
  
  // Form State
  const [basics, setBasics] = useState({ title: '', description: '', location: '', remote: false, salaryMin: '', salaryMax: '' })
  const [skillInput, setSkillInput] = useState('')
  const [skills, setSkills] = useState<{name: string, required: boolean}[]>([])

  const addSkill = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && skillInput.trim()) {
      e.preventDefault()
      if (!skills.find(s => s.name.toLowerCase() === skillInput.toLowerCase())) {
        setSkills([...skills, { name: skillInput.trim(), required: true }])
      }
      setSkillInput('')
    }
  }

  const toggleSkillImportance = (name: string) => {
    setSkills(skills.map(s => s.name === name ? { ...s, required: !s.required } : s))
  }

  const removeSkill = (name: string) => {
    setSkills(skills.filter(s => s.name !== name))
  }

  const handlePublish = async () => {
    try {
      // Typically API post logic here mapping to schemas.JobCreate
      await api.post('/employers/post-job', { ...basics, skills })
      navigate('/employer/jobs')
    } catch (err) {
      console.error(err)
      navigate('/employer/jobs')
    }
  }

  return (
    <div className="max-w-3xl mx-auto py-8">
      {/* Stepper tracking */}
      <div className="flex justify-between items-center mb-12 relative">
        <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-200 -z-10 rounded-full transform -translate-y-1/2"></div>
        <div className="absolute top-1/2 left-0 h-1 bg-brand-500 -z-10 rounded-full transform -translate-y-1/2 transition-all duration-700 ease-out" style={{ width: `${(step - 1) * 50}%` }}></div>
        
        {[1, 2, 3].map(i => (
          <div key={i} className={`w-10 h-10 rounded-full flex items-center justify-center font-black text-sm transition-all duration-500 border-4 border-white ${step >= i ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/30 scale-110' : 'bg-slate-200 text-slate-400'}`}>
            {step > i ? <Check className="w-5 h-5"/> : i}
          </div>
        ))}
      </div>

      <div className="glass-panel p-10 min-h-[450px] shadow-2xl border-white/60">
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="1" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
              <h2 className="text-3xl font-bold text-slate-800 mb-8">Job Basics</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2 uppercase tracking-wide">Job Title</label>
                  <input type="text" className="w-full px-5 py-4 rounded-xl border border-slate-200 focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 outline-none transition-all font-medium" placeholder="e.g. Senior AI Engineer" value={basics.title} onChange={e => setBasics({...basics, title: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2 uppercase tracking-wide">Description</label>
                  <textarea rows={4} className="w-full px-5 py-4 rounded-xl border border-slate-200 focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 outline-none transition-all resize-none font-medium" placeholder="Describe the role responsibilities..." value={basics.description} onChange={e => setBasics({...basics, description: e.target.value})} />
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                     <label className="block text-sm font-bold text-slate-700 mb-2 uppercase tracking-wide"><MapPin className="w-4 h-4 inline mr-1 text-slate-400"/> Location</label>
                     <input type="text" className="w-full px-5 py-4 rounded-xl border border-slate-200 outline-none focus:ring-4 focus:ring-brand-500/20 font-medium" placeholder="City, State" value={basics.location} onChange={e => setBasics({...basics, location: e.target.value})} />
                  </div>
                  <div>
                     <label className="block text-sm font-bold text-slate-700 mb-2 uppercase tracking-wide"><DollarSign className="w-4 h-4 inline mr-1 text-slate-400"/> Salary Range</label>
                     <div className="flex items-center gap-3">
                       <input type="number" className="w-full px-5 py-4 rounded-xl border border-slate-200 outline-none font-medium text-center" placeholder="Min" value={basics.salaryMin} onChange={e => setBasics({...basics, salaryMin: e.target.value})} />
                       <span className="text-slate-300 font-bold">-</span>
                       <input type="number" className="w-full px-5 py-4 rounded-xl border border-slate-200 outline-none font-medium text-center" placeholder="Max" value={basics.salaryMax} onChange={e => setBasics({...basics, salaryMax: e.target.value})} />
                     </div>
                  </div>
                </div>
                <div className="flex items-center gap-3 mt-4 p-5 bg-brand-50/50 rounded-xl border border-brand-100 hover:bg-brand-50 transition-colors cursor-pointer" onClick={() => setBasics({...basics, remote: !basics.remote})}>
                  <input type="checkbox" id="remote" className="w-6 h-6 rounded-md border-slate-300 text-brand-600 focus:ring-brand-500 cursor-pointer" checked={basics.remote} onChange={() => {}} />
                  <label className="font-bold text-brand-900 cursor-pointer">This role allows remote work globally</label>
                </div>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="2" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
              <h2 className="text-3xl font-bold text-slate-800 mb-3">Define Required Skills</h2>
              <p className="text-slate-500 mb-10 font-medium leading-relaxed">AI Mapping will automatically cross-reference these against the vast ESCO database to match candidates mathematically.</p>
              
              <div className="relative mb-10 group">
                <input 
                  type="text" 
                  className="w-full px-6 py-5 pl-14 rounded-2xl border-2 border-slate-200 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 outline-none shadow-sm text-xl font-bold transition-all text-slate-700" 
                  placeholder="Type a skill and press Enter..." 
                  value={skillInput} 
                  onChange={e => setSkillInput(e.target.value)} 
                  onKeyDown={addSkill} 
                />
                <PlusCircle className="absolute left-5 top-1/2 transform -translate-y-1/2 text-slate-300 group-focus-within:text-brand-500 w-7 h-7 transition-colors" />
              </div>

              <div className="space-y-4">
                {skills.length === 0 && <div className="text-center p-10 border-2 border-dashed border-slate-200 rounded-2xl text-slate-400 font-bold bg-slate-50/50">No skills added. Press enter to add requirements.</div>}
                
                <AnimatePresence>
                  {skills.map(skill => (
                    <motion.div initial={{opacity: 0, y: -10, scale: 0.95}} animate={{opacity: 1, y: 0, scale: 1}} exit={{opacity: 0, scale: 0.9}} key={skill.name} className="flex items-center justify-between p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:border-brand-300 hover:shadow-md transition-all">
                      <span className="font-bold text-slate-800 text-xl">{skill.name}</span>
                      <div className="flex items-center gap-4">
                        <div className="flex bg-slate-100 p-1 rounded-xl">
                          <button onClick={() => toggleSkillImportance(skill.name)} className={`px-5 py-2 rounded-lg text-sm font-bold transition-all ${skill.required ? 'bg-rose-100 text-rose-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Required</button>
                          <button onClick={() => toggleSkillImportance(skill.name)} className={`px-5 py-2 rounded-lg text-sm font-bold transition-all ${!skill.required ? 'bg-amber-100 text-amber-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Preferred</button>
                        </div>
                        <button onClick={() => removeSkill(skill.name)} className="p-2.5 text-slate-400 hover:text-white hover:bg-rose-500 rounded-full transition-colors"><X className="w-5 h-5"/></button>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="3" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
              <h2 className="text-3xl font-bold text-slate-800 mb-8">Review & Publish</h2>
              <div className="bg-slate-50 rounded-3xl p-8 border border-slate-200 mb-6 space-y-6 shadow-md relative overflow-hidden">
                 <div className="absolute top-0 left-0 w-2 h-full bg-brand-500"></div>
                <div className="flex justify-between items-start border-b border-slate-200 pb-6">
                  <div>
                    <h3 className="text-3xl font-black text-slate-900 tracking-tight">{basics.title || 'Untitled Role'}</h3>
                    <p className="text-slate-500 font-bold text-lg mt-2">{basics.location} {basics.remote && <span className="text-brand-600 bg-brand-50 px-2 py-1 rounded ml-2">Remote Allowed</span>}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-black text-emerald-600">${basics.salaryMin}k - ${basics.salaryMax}k</span>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">Required Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {skills.filter(s => s.required).map(s => <span key={s.name} className="badge-red px-4 py-1.5 shadow-sm">{s.name}</span>)}
                    {skills.filter(s => s.required).length === 0 && <span className="text-sm font-bold text-slate-400">None</span>}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mt-6 mb-3">Preferred Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {skills.filter(s => !s.required).map(s => <span key={s.name} className="badge-amber px-4 py-1.5 shadow-sm">{s.name}</span>)}
                    {skills.filter(s => !s.required).length === 0 && <span className="text-sm font-bold text-slate-400">None</span>}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex justify-between mt-12 pt-8 border-t border-slate-100">
          <button onClick={() => setStep(step - 1)} disabled={step === 1} className={`btn-secondary font-bold text-lg px-8 py-3 flex items-center gap-2 ${step === 1 ? 'opacity-0 invisible' : ''}`}>
             <ArrowLeft className="w-5 h-5" /> Back
          </button>
          
          {step < 3 ? (
            <button onClick={() => setStep(step + 1)} className="btn-primary font-bold text-lg px-8 py-3 flex items-center gap-2 shadow-brand-500/30">
              Continue <ArrowRight className="w-5 h-5" />
            </button>
          ) : (
            <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={handlePublish} className="btn-primary text-xl px-12 py-4 flex items-center gap-3 bg-gradient-to-r from-emerald-500 to-teal-600 border-none shadow-xl shadow-emerald-500/30 hover:from-emerald-400 hover:to-teal-500">
              <Check className="w-6 h-6 border-2 rounded-full border-white" /> Publish Listing To Engine
            </motion.button>
          )}
        </div>
      </div>
    </div>
  )
}
