export default function GameControls({ onChoice }) {
    const choices = ['🪨 Камень', '📄 Бумага', '✂️ Ножницы']; // Используем русские названия с эмодзи
  
    return (
      <div className="game-controls">
        <div className="variant">
          <h3>Выберите вариант:</h3>
        </div>
        <div className="choices-container">
          {choices.map((choice) => (
            <button className="choice-button"
              key={choice}
              onClick={() => onChoice(choice)}
              aria-label={choice.replace(/[^а-яА-Я]/g, '')} // Для доступности (оставляем только текст)
            >
              {choice}
            </button>
          ))}
        </div>
      </div>
    );
  }