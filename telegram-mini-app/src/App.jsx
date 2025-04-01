import { useEffect, useState } from 'react';
import { WebApp } from '@twa-dev/sdk';
import './App.css';

function App() {
  const [user, setUser] = useState(null); //user name из тг
  const [inputValue, setInputValue] = useState('');
  const [theme, setTheme] = useState('light'); // тема веб приложения светлая

  useEffect(() => {
    WebApp.ready(); //тг прил готово 
    WebApp.expand(); //веб прил занимает весь занимаемый экран
  })
}