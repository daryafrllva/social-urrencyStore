export default function GameModal({ result, onClose, explanation, reward = 0 }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {result === 'win' ? (
          <>
            <h2>Поздравляем! 🎉</h2>
            <p>Вы нашли монетку и выиграли 10 джоинов или каких там монет!</p>
            {}
            {reward > 0 && (
              <div className="reward-message">
                Вы заработали: <span className="reward-amount">{reward} монет</span>
              </div>
            )}


            <div className="modal-buttons">
              <button 
                onClick={onClose} 
                className="modal-button win"
              >
                Забрать приз
              </button>
              </div>
            {explanation && (
              <div className="modal-explanation">
                <p>{explanation}</p>
              </div>
            )}
          </>
            
        ) : (
          <>
            <h2>Увы! 😕</h2>
            <p>Вы не нашли монетку. Попробуйте снова!</p>
            <div className="modal-buttons">
              <button 
                onClick={onClose} 
                className="modal-button lose"
              >
                В главное меню
              </button>
            </div>
            {explanation && (
              <div className="modal-explanation">
                <p>{explanation}</p>
              </div>
              
            )}
          </>
        )}
      </div>
    </div>
  );
}