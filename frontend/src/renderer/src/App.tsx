import { HashRouter, Routes, Route, useLocation } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { ToastProvider } from './contexts/ToastContext'
import { ProjectProvider } from './contexts/ProjectContext'
import { AppLayout } from './components/layout/AppLayout'
import { ErrorBoundary } from './components/ErrorBoundary'

// Pages
import { Home } from './pages/Home'
import { Dashboard } from './pages/Dashboard'
import { Library } from './pages/Library'
import { Templates } from './pages/Templates'
import { Processing } from './pages/Processing'
import { Settings } from './pages/Settings'
import { ExportProfiles } from './pages/ExportProfiles'
import { Logs } from './pages/Logs'
import { SubtitlePresets } from './pages/SubtitlePresets'

import { Assets } from './pages/Assets'

// The key resets the boundary on navigation, so leaving a broken screen recovers the app.
function AppRoutes() {
  const location = useLocation()

  return (
    <ErrorBoundary key={location.pathname}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/library" element={<Library />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/templates" element={<Templates />} />
        <Route path="/subtitle-presets" element={<SubtitlePresets />} />
        <Route path="/processing" element={<Processing />} />
        <Route path="/export-profiles" element={<ExportProfiles />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/logs" element={<Logs />} />
      </Routes>
    </ErrorBoundary>
  )
}

function App() {
  return (
    <ToastProvider>
      <ProjectProvider>
        <ThemeProvider>
          <HashRouter>
            <AppLayout>
              <AppRoutes />
            </AppLayout>
          </HashRouter>
        </ThemeProvider>
      </ProjectProvider>
    </ToastProvider>
  )
}

export default App
