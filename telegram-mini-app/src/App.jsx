import { useState } from "react";
import RockPaperScissors from "./assets/components/game/RockPaperScissors";
import CoinGame from "./assets/components/game/CoinGame";
import "./styles/game.css"; 
import "./App.css";

export default function App() {
  const [currentGame, setCurrentGame] = useState(null); 
  const [userBalance, setUserBalance] = useState(0); //Для добавления счёта

  const addCoins = (amount) => {
    setUserBalance(prev => prev + amount);
  };


  const renderGame = () => {
    switch(currentGame) {
      case 'rps':
        return <RockPaperScissors 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => addCoins(5)} // 5 монет за победу в RPS
               />;
      case 'coin':
        return <CoinGame 
                 onExit={() => setCurrentGame(null)} 
                 onWin={() => addCoins(10)} // 10 монет за победу в CoinGame
               />;
      
      
               default:
                return (
                  <div className="home-screen">
                    <div className="wallet-container">
                      <WalletIcon className="wallet-icon" />
                      <span className="wallet-amount">{userBalance}</span>
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
                    </div>
                  </div>
                );
            }
          };
          console.log("Render check:", { currentGame, userBalance });
          return (
            <div className="app-container">
              {renderGame()}
            </div>
          );
  }