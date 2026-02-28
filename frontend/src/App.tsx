import { Suspense, lazy } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from './components/common/AppLayout'
import { LoadingState } from './components/common/LoadingState'

const PrescriptionUploadPage = lazy(() =>
  import('./pages/PrescriptionUploadPage').then((module) => ({
    default: module.PrescriptionUploadPage,
  })),
)

const RiskDashboardPage = lazy(() =>
  import('./pages/RiskDashboardPage').then((module) => ({
    default: module.RiskDashboardPage,
  })),
)

const App = () => {
  return (
    <Suspense fallback={<div className="mx-auto max-w-7xl p-6"><LoadingState /></div>}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<PrescriptionUploadPage />} />
          <Route path="/dashboard" element={<RiskDashboardPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Suspense>
  )
}

export default App
