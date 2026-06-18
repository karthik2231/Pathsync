import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import App from './App'
import Onboarding from './components/Onboarding'
import CandidateDashboard from './components/CandidateDashboard'
import GapReport from './components/GapReport'
import EmployerPostJob from './components/EmployerPostJob'
import EmployerJobs from './components/EmployerJobs'
import EmployerShortlist from './components/EmployerShortlist'
import './index.css'

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<Navigate to="/onboarding" replace />} />
            <Route path="onboarding" element={<Onboarding />} />
            <Route path="dashboard" element={<CandidateDashboard />} />
            <Route path="jobs/:jobId/gap-report" element={<GapReport />} />
            
            <Route path="employer/post-job" element={<EmployerPostJob />} />
            <Route path="employer/jobs" element={<EmployerJobs />} />
            <Route path="employer/jobs/:jobId/candidates" element={<EmployerShortlist />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
