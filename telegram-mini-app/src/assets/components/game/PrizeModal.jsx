export default function PrizeModal({ onClose, onConfirm }) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <h2>Поздравляем! 🎉</h2>
          <p>Вы выиграли 10 игровых монет!</p>
          
          <div className="modal-buttons">
            <button onClick={onClose} className="cancel-button">
              Отмена
            </button>
            <button onClick={onConfirm} className="confirm-button">
              Забрать приз
            </button>
          </div>
        </div>
      </div>
    );
  }