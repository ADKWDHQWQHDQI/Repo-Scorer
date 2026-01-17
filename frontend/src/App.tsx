import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { WelcomePage } from './pages/WelcomePage'
import { PlatformSelectionPage } from './pages/PlatformSelectionPage'
import { EmailCapturePage } from './pages/EmailCapturePage'
import { AssessmentPage } from './pages/AssessmentPage'
import { ResultsPage } from './pages/ResultsPage'
import { PublicResultsPage } from './pages/PublicResultsPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/platform-selection" element={<PlatformSelectionPage />} />
        <Route path="/email" element={<EmailCapturePage />} />
        <Route path="/assessment" element={<AssessmentPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/shared/:shareToken" element={<PublicResultsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
