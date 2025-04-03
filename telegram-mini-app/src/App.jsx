import { useState } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import CoinGame from "./assets/components/game/CoinGame";
import "./styles/game.css"; 
import "./App.css";
import './assets/fonts/fonts.css';

export default function App() {
  const [currentGame, setCurrentGame] = useState(null); 
    
  const renderGame = () => {
    switch(currentGame) {
      case 'rps':
        return <RockPaperScissors onExit={() => setCurrentGame(null)} />;
      case 'coin':
        return <CoinGame onExit={() => setCurrentGame(null)} />;
      
      
        default:
        return (
            <div className="home-screen">
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
                <button className="start-game-button"
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
                <button className="start-game-button"
                        onClick={() => setCurrentGame('coin')}>
                        Играть: Угадай где монетка
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