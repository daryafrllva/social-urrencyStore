



























































































import { useState, useEffect } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import CoinGame from "./assets/components/game/CoinGame";
import QuizGame from "./assets/components/game/QuizGame";
import "./styles/game.css"; 
import "./App.css";

// Функция для GET-запроса (можно вынести в отдельный файл api.js)
const fetchUserBalance = async (userId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/balance?userId=${userId}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching user balance:', error);
    return { balance: 0 }; // Возвращаем 0 в случае ошибки
  }
};

export default function App() {
  const [currentGame, setCurrentGame] = useState(null);
  const [userBalance, setUserBalance] = useState(0); 
  const [userId, setUserId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.expand();
      tg.enableClosingConfirmation();
      
      if (tg.initDataUnsafe?.user) {
        const user = tg.initDataUnsafe.user;
        setUserId(user.id);
        
        // Загружаем баланс пользователя при инициализации
        fetchUserBalance(user.id)
          .then(data => {
            setUserBalance(data.balance);
            setIsLoading(false);
          })
          .catch(() => setIsLoading(false));
      } else {
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const sendDataToTelegram = (data) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.sendData(JSON.stringify(data));
    }
  };

  const handleGameComplete = (reward) => {
    setUserBalance(prev => {
      const newBalance = prev + reward;
      sendDataToTelegram({
        action: 'update_balance',
        userId,
        newBalance,
        reward
      });
      return newBalance;
    });
  };

  const renderGame = () => {
    if (isLoading) {
      return <div className="loading">Загрузка...</div>;
    }

    switch(currentGame) {
      case 'rps':
        return <RockPaperScissors 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => handleGameComplete(5)}
               />;
      case 'coin':
        return <CoinGame 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => handleGameComplete(10)}
               />;
      case 'quiz': 
        return <QuizGame 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => handleGameComplete(15)}
               />;
      default:
        return (
          <div className="home-screen">
            <div className="tg-balance">
              <span>Баланс: {userBalance} монет</span>
              {window.Telegram?.WebApp && (
                <button 
                  onClick={() => sendDataToTelegram({ action: 'close_app' })}
                  className="tg-close-btn"
                >
                  Закрыть
                </button>
              )}
            </div>
            
            <h1>Выберите игру</h1>
            <div className="game-buttons">
              <button 
                onClick={() => setCurrentGame('rps')}
                className="game-button"
              >
                Камень-Ножницы-Бумага (+5 монет)
              </button>
              <button 
                onClick={() => setCurrentGame('coin')}
                className="game-button"
              >
                Угадай монетку (+10 монет)
              </button>
              <button 
                onClick={() => setCurrentGame('quiz')}
                className="game-button"
              >
                Викторина (+15 монет)
              </button>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="app-container">
      {renderGame()}
    </div>
  );
}