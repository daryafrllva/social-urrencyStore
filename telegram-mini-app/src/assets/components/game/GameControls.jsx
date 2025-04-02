export default function GameControls({ onChoice }) {
    const choices = ['🪨 Камень', '📄 Бумага', '✂️ Ножницы']; // Используем русские названия с эмодзи
  
    return (
      <div className="game-controls">
        <h3>Выберите вариант:</h3>
        <div className="choices-container">
          {choices.map((choice) => (
            <button
              key={choice}
              onClick={() => onChoice(choice)}
              className="choice-button"
              aria-label={choice.replace(/[^а-яА-Я]/g, '')} // Для доступности (оставляем только текст)
            >
              {choice}
            </button>
          ))}
        </div>
      </div>
    );
  }