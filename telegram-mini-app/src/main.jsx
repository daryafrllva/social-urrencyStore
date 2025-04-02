import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

<<<<<<< HEAD
// Подключаем шрифт Montserrat
import '@fontsource/montserrat/400.css'; // Regular
import '@fontsource/montserrat/500.css'; // Medium
import '@fontsource/montserrat/700.css'; // Bold

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Не найден элемент с id "root"');
}

createRoot(rootElement).render(
=======
createRoot(document.getElementById('root')).render(
>>>>>>> 0d3f2f89aac5f493915c50cc02642fd628ca6d54
  <StrictMode>
    <App />
  </StrictMode>,
)
