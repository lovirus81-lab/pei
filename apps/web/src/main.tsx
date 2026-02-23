import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ReactFlowProvider } from 'reactflow'
import 'reactflow/dist/style.css'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary.tsx'

// Visual Probe: Verify main.tsx execution
const probe = document.createElement('div');
probe.style.position = 'fixed';
probe.style.top = '0';
probe.style.left = '0';
probe.style.zIndex = '9999';
probe.style.background = 'yellow';
probe.style.color = 'black';
probe.style.padding = '10px';
probe.style.fontWeight = 'bold';
probe.textContent = 'MAIN.TSX LOADED';
document.body.appendChild(probe);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ReactFlowProvider>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </ReactFlowProvider>
  </StrictMode>,
)
