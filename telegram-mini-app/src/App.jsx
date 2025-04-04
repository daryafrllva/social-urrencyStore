import { useState, useEffect } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import CoinGame from "./assets/components/game/CoinGame";
import QuizGame from "./assets/components/game/QuizGame";
import "./styles/game.css"; 
import "./App.css";
import './assets/fonts/fonts.css';

export default function App() {
  const [currentGame, setCurrentGame] = useState(null);
  const [userBalance, setUserBalance] = useState(0); 
  const [chatId, setChatId] = useState(null);

  useEffect(() => {
    // Пробуем получить chat_id из URL параметров
    const params = new URLSearchParams(window.location.search);
    const urlChatId = params.get('chat_id');
    if (urlChatId) {
      setChatId(urlChatId);
    } else {
      // Если нет в URL, пробуем получить из Telegram WebApp
      const tg = window.Telegram?.WebApp;
      if (tg) {
        tg.expand();
        tg.enableClosingConfirmation();
        
        if (tg.initDataUnsafe?.user) {
          setChatId(tg.initDataUnsafe.user.id.toString());
        } else if (tg.initDataUnsafe?.chat) {
          setChatId(tg.initDataUnsafe.chat.id.toString());
        }
      }
    }
  }, []);
  
  const sendDataToTelegram = (data) => {
    if (window.Telegram?.WebApp) {
      // Формируем данные для отправки на бэкенд
      const backendData = {
        user_id: parseInt(chatId), // Преобразуем в число для бэкенда
        amount: data.amount,       // Сумма для изменения баланса
        action: data.action,      // Действие (coins_earned и т.д.)
        newBalance: data.newBalance // Новый баланс (опционально)
      };
      
      // Отправляем данные в Telegram WebApp и на бэкенд
      window.Telegram.WebApp.sendData(JSON.stringify(backendData));
      
      // Дополнительно можно отправить запрос напрямую на бэкенд
      fetch('http://localhost:8000/api/update_balance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: parseInt(chatId),
          amount: data.amount
        })
      })
      .then(response => response.json())
      .then(data => console.log('Balance updated:', data))
      .catch(error => console.error('Error updating balance:', error));
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
                <div className="tasks__more">
                  <h2>Больше заданий нет</h2>
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
//в ссылке передаём две переменные 