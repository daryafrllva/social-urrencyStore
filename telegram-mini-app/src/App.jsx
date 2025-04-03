import { useState } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import "./styles/game.css"; // Общие стили
import "./App.css";

export default function App() {
  const [showGame, setShowGame] = useState(false); // Управление отображением игры

  return (
    <div className="app-container"> // Можно трогать
      {!showGame ? (
        // Главный экран с кнопкой запуска
        <div className="home-screen">
          <h1>Добро пожаловать!</h1>
         
          <button 
            onClick={() => setShowGame(true)}
            className="start-game-button"
          >
            Играть в "Камень-Ножницы-Бумага"
          </button>
          <button 
            onClick={() => setShowGame(true)}
            className="start-game-button"
          >
            Играть в "Угадай"
          </button>
          <button 
            onClick={() => setShowGame(true)}
            className="start-game-button"
          >
            Играть в "Викторину"
          </button>

        </div>
      ) : (
        // Компонент игры (передаем функцию для возврата)
        <RockPaperScissors onExit={() => setShowGame(false)} />
      )}

      <div>
      <h1>Hello, Telegram Mini App!</h1>
      <button onClick={sendDataToBot}>
        Send Data to Bot
      </button>
    </div>
    
    </div>
  );
}