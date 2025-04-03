



























































































import { useState, useEffect } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import CoinGame from "./assets/components/game/CoinGame";
import QuizGame from "./assets/components/game/QuizGame";
import "./styles/game.css"; 
import "./App.css";

export default function App() {
  const [currentGame, setCurrentGame] = useState(null);
  const [userBalance, setUserBalance] = useState(0); 

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.expand();
      tg.enableClosingConfirmation();
      console.log('Telegram WebApp initialized:', tg.initData);
      
      
      if (tg.initDataUnsafe?.user) {
        console.log('User data:', tg.initDataUnsafe.user);
      }
    }
  }, []);

 
  const sendDataToTelegram = (data) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.sendData(JSON.stringify(data));
    }
  };

  const addCoins = (amount) => {
    setUserBalance(prev => {
      const newBalance = prev + amount;
      sendDataToTelegram({
        action: 'coins_earned',
        amount: amount,
        newBalance: newBalance
      });
      return newBalance;
    });
  };

  const renderGame = () => {
    switch(currentGame) {
      case 'rps':
        return <RockPaperScissors 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => addCoins(5)} // 10 монет за победу
               />;
      case 'coin':
        return <CoinGame 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => addCoins(10)} // 5 монет за победу
               />;
      case 'quiz': 
      return <QuizGame 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => addCoins(15)} // 5 монет за победу
               />;
      
      default:
        return (
          <div className="home-screen">
            {}
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
            
            <h1>Задания, чтобы заработать монеты</h1>
            <div className="game-buttons">
              <button 
                onClick={() => setCurrentGame('rps')}
                className="game-button"
              >
                Камень-Ножницы-Бумага
              </button>
              <button 
                onClick={() => setCurrentGame('coin')}
                className="game-button"
              >
                Угадай где монетка
              </button>
              <button 
                onClick={() => setCurrentGame('quiz')}
                className="game-button"
              >
                Викторина
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