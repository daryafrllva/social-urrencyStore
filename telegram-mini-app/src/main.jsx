import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import { init, miniApp } from '@telegram-apps/sdk';

const initializeTelegramWebApp = async () => {
  try {
    // Инициализация SDK
    await init();
    
    // Проверка доступности Mini App API
    if (miniApp.ready.isAvailable()) {
      await miniApp.ready();
      console.log('Mini App инициализировано');
      
      // Основные настройки WebApp
      if (window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        
        // Раскрытие на весь экран
        tg.expand();
        
        // Установка цвета заголовка
        tg.setHeaderColor('#fcb69f');
        
        // Подтверждение при закрытии
        tg.enableClosingConfirmation();
        
        // Дополнительные настройки
        tg.BackButton.hide();
        tg.MainButton.hide();
        
        console.log('Telegram WebApp настроен');
      }
    }
  } catch (error) {
    console.error('Ошибка инициализации:', error);
    
    // Режим для разработки вне Telegram
    if (import.meta.env.MODE === 'development') { // Используем Vite-совместимый способ
      console.warn('Работаем в dev-режиме без Telegram WebApp');
    }
  }
};

// Вызываем инициализацию перед рендерингом
initializeTelegramWebApp().then(() => {
  createRoot(document.getElementById('root')).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
});