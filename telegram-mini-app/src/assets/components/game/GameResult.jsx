export default function GameResult({ result, onReset, showPrize, onClaimPrize }) {
    return (
      <div className="game-result">
        <div className="choices">
          <p>Ваш выбор: <strong>{result.playerChoice}</strong></p>
          <p>Выбор компьютера: <strong>{result.computerChoice}</strong></p>
        </div>
        
        <h2 className={`result-${result.gameResult.toLowerCase()}`}>
          {result.gameResult.toUpperCase()}
        </h2>
  
        <div className="action-buttons">
          <button onClick={onReset} className="reset-button">
            Играть снова
          </button>
          
          {showPrize && (
            <button onClick={onClaimPrize} className="prize-button">
              Получить приз 🎁
            </button>
          )}
        </div>
      </div>
    );
  }