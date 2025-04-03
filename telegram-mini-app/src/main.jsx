import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

// Подключаем шрифт Montserrat
import '@fontsource/montserrat/400.css'; // Regular
import '@fontsource/montserrat/500.css'; // Medium
import '@fontsource/montserrat/700.css'; // Bold

const rootElement = document.getElementById('root');

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
