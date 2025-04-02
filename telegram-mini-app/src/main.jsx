import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';

// Подключаем шрифт Montserrat
import '@fontsource/montserrat/400.css'; // Regular
import '@fontsource/montserrat/500.css'; // Medium
import '@fontsource/montserrat/700.css'; // Bold

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Не найден элемент с id "root"');
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>
);