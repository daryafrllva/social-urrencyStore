import { useState, useEffect } from 'react';
import '../../../styles/coin-game.css';
import GameModal from './GameModal';

export default function CoinGame({ onExit, /*onWin*/ }) {
  const [grid, setGrid] = useState(Array(9).fill(null));
  const [coinPosition, setCoinPosition] = useState(null);
  const [gameEnded, setGameEnded] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [gameResult, setGameResult] = useState(null); 

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = () => {
    const newCoinPosition = Math.floor(Math.random() * 9);
    setCoinPosition(newCoinPosition);
    setGrid(Array(9).fill(null));
   
    setGameEnded(false);
    setGameResult(null);
  };

  const handleSquareClick = (index) => {
    if (gameEnded) return;

    const newGrid = [...grid];
    newGrid[index] = 'checked';
    setGrid(newGrid);

    if (index === coinPosition) {
      newGrid[index] = 'coin';
      setGameResult('win');
     // onWin();
    } else {
      setGameResult('lose');
    }

    setGameEnded(true);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    onExit();
  };

  return (
    <div className="coin-game-container">
      <button onClick={onExit} className="exit-button">
        ← Назад
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