import { useState, useEffect } from 'react';
import '../../../styles/coin-game.css';
import GameModal from './GameModal';

export default function CoinGame({ onExit, onWin }) {
  const [grid, setGrid] = useState(Array(9).fill(null));
  const [coinPosition, setCoinPosition] = useState(null);
  const [gameEnded, setGameEnded] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [tgReady, setTgReady] = useState(false);
  const [prizeClaimed, setPrizeClaimed] = useState(false);

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.expand();
      setTgReady(true);
    }
  }, []);

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = () => {
    const newCoinPosition = Math.floor(Math.random() * 9);
    setCoinPosition(newCoinPosition);
    setGrid(Array(9).fill(null));
    setGameEnded(false);
    setGameResult(null);
    setPrizeClaimed(false);
  };

  const handleSquareClick = (index) => {
    if (gameEnded) return;

    const newGrid = [...grid];
    newGrid[index] = 'checked';
    setGrid(newGrid);

    if (index === coinPosition) {
      newGrid[index] = 'coin';
      setGameResult('win');
      if (!prizeClaimed) {
        onWin(); // Начисляем монеты при победе
      }
    } else {
      setGameResult('lose');
    }

    setGameEnded(true);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    if (gameResult === 'win') {
      
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.sendData(JSON.stringify({
          action: 'prize_claimed',
          game: 'coin_game',
          prize: 10
        }));
      }
    }
    onExit();
  };

  return (
    <div className="coin-game-container">
      {tgReady && (
        <button 
          onClick={() => window.Telegram?.WebApp?.close()}
          className="tg-close-btn"
        >
          Закрыть игру
        </button>
      )}
      
      <button onClick={onExit} className="back-button">
        ← На главную
      </button>

      <h2>Найди монетку!</h2>
      <p>{!gameEnded ? 'Выбери квадрат, где спрятана монетка!' : ''}</p>

      <div className="grid">
        {grid.map((square, index) => (
          <div
            key={index}
            className={`square ${square || 'empty'}`}
            onClick={() => handleSquareClick(index)}
          >
            {square === 'coin' && '💰'}
            {square === 'checked' && '❌'}
          </div>
        ))}
      </div>

      {showModal && (
        <GameModal 
          result={gameResult}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
}