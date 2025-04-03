import { useState } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import CoinGame from "./assets/components/game/CoinGame";
import "./styles/game.css"; 
import "./App.css";

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