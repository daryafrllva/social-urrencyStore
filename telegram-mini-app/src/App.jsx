import { useState } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import "./styles/game.css"; // Общие стили

export default function App() {
  const [showGame, setShowGame] = useState(false); // Управление отображением игры

  return (
    <div className="app-container">
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
        </div>
      ) : (
        // Компонент игры (передаем функцию для возврата)
        <RockPaperScissors onExit={() => setShowGame(false)} />
      )}
    </div>
  );
}