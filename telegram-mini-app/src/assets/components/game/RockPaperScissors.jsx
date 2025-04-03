import { useState } from 'react';
import GameControls from './GameControls';
import GameResult from './GameResult';
import PrizeModal from './PrizeModal';
import '../../../styles/game.css';

export default function RockPaperScissors({ onExit }) {
  // Состояния игры
  const [result, setResult] = useState(null);
  const [showPrize, setShowPrize] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [prizeClaimed, setPrizeClaimed] = useState(false);

 
  const handleChoice = (playerChoice) => {
    const choices = ['🪨 Камень', '📄 Бумага', '✂️ Ножницы'];
    const computerChoice = choices[Math.floor(Math.random() * choices.length)];
    const gameResult = determineWinner(playerChoice, computerChoice);
    
    setResult({ 
      playerChoice, 
      computerChoice, 
      gameResult 
    });
    setShowPrize(gameResult === 'Победа');
  };

 
  const determineWinner = (player, computer) => {
    if (player === computer) return 'Ничья';
    if (
      (player === '🪨 Камень' && computer === '✂️ Ножницы') ||
      (player === '📄 Бумага' && computer === '🪨 Камень') ||
      (player === '✂️ Ножницы' && computer === '📄 Бумага')
    ) {
      return 'Победа';
    }
    return 'Поражение';
  };

  
  const resetGame = () => {
    setResult(null);
    setShowPrize(false);
    setPrizeClaimed(false);
  };

  const claimPrize = () => {
    setShowModal(true);
  };

  const confirmClaim = () => {
    setPrizeClaimed(true);
    setShowModal(false);
    alert('Приз получен! +10 монет');
  };

  return (
    <div className="game-screen">
      <button onClick={onExit} className="back-button">
        ← На главную
      </button>

      <h1>Камень-Ножницы-Бумага</h1>

      {!result ? (
        <GameControls onChoice={handleChoice} />
      ) : (
        <GameResult
          result={result}
          onReset={resetGame}
          showPrize={showPrize && !prizeClaimed}
          onClaimPrize={claimPrize}
        />
      )}

      {showModal && (
        <PrizeModal
          onClose={() => setShowModal(false)}
          onConfirm={confirmClaim}
        />
      )}
    </div>
  );
}