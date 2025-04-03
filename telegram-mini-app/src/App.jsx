import { useState, useEffect } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import CoinGame from "./assets/components/game/CoinGame";
import QuizGame from "./assets/components/game/QuizGame";
import "./styles/game.css"; 
import "./App.css";
import './assets/fonts/fonts.css';

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
                    <button className="tg-close-btn"
                      onClick={() => sendDataToTelegram({ action: 'close_app' })}>
                      Закрыть
                    </button>
                  )}
                </div>
                <h1>Задания, чтобы заработать монеты</h1>

                <div class="task__blank">
                    <div className="squares">
                        <div class="task__text">
                            <div class="task__name">
                                <p>Камень, ножницы,бумага</p>
                            </div>
                            <div class="task__description">
                                <p>Удержи победную серию 5 раз подряд и получи свою награду</p>
                            </div>
                            <div class="task__owner">
                                <p>Игра: Камень, ножницы, бумага</p>
                            </div>
                        </div>
                        <div class="task__joule">
                            <div class="task__icon">
                                <img src="/images/Vector.png" alt="Тут молния" />
                            </div>
                            <div class="task__price">
                                <p>500</p>
                            </div>
                        </div>
                    </div>
                    <button className="game-button"
                        onClick={() => setCurrentGame('rps')}>
                        Играть: Камень-Ножницы-Бумага
                    </button>
                </div>

                <div class="task__blank">
                    <div className="squares">
                        <div class="task__text">
                            <div class="task__name">
                                <p>Угадай где монетка</p>
                            </div>
                            <div class="task__description">
                                <p>Победи в игре 5 раз подряд и получи свою награду</p>
                            </div>
                            <div class="task__owner">
                                <p>Игра: угадай, где монетка</p>
                            </div>
                        </div>
                        <div class="task__joule">
                            <div class="task__icon">
                                <img src="/images/Vector.png" alt="Тут молния" />
                            </div>
                            <div class="task__price">
                                <p>500</p>
                            </div>
                        </div>
                    </div>
                    <button className="game-button"
                            onClick={() => setCurrentGame('coin')}>
                            Играть: Угадай где монетка
                    </button>
                </div>

                <div class="task__blank">
                    <div className="squares">
                        <div class="task__text">
                            <div class="task__name">
                                <p>Викторина</p>
                            </div>
                            <div class="task__description">
                                <p>Победи в игре 5 раз подряд и получи свою награду</p>
                            </div>
                            <div class="task__owner">
                                <p>Игра: Викторина</p>
                            </div>
                        </div>
                        <div class="task__joule">
                            <div class="task__icon">
                                <img src="/images/Vector.png" alt="Тут молния" />
                            </div>
                            <div class="task__price">
                                <p>500</p>
                            </div>
                        </div>
                    </div>
                    <button className="game-button"
                            onClick={() => setCurrentGame('quiz')}>
                            Играть: Викторина
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