import { useState, useEffect } from 'react';
import GameModal from './GameModal';
import '../../../styles/quiz-game.css';

const quizThemes = [
  { id: 1, name: 'Животные' },
  { id: 2, name: 'Наука' },
  { id: 3, name: 'История' },
  { id: 4, name: 'География' },
  { id: 5, name: 'Искусство' },
  { id: 6, name: 'Спорт' },
];

export default function QuizGame({ onExit }) {
  const [currentTheme, setCurrentTheme] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [currentExplanation, setCurrentExplanation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [questionQueue, setQuestionQueue] = useState([]);

  // Функция для генерации вопроса через API
  const generateQuestion = async (themeName) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://192.168.0.38:8000/api/generate-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category: themeName })
      });
      
      const newQuestion = await response.json();
      return newQuestion;
    } catch (error) {
      console.error('Ошибка генерации вопроса:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const handleThemeSelect = async (themeId) => {
    const themeName = quizThemes.find(t => t.id === themeId).name;
    setCurrentTheme(themeId);
    
    // Генерируем первый вопрос сразу
    const firstQuestion = await generateQuestion(themeName);
    if (firstQuestion) {
      setCurrentQuestion(firstQuestion);
      setQuestionQueue([]);
      
      // Начинаем фоновую загрузку следующего вопроса
      loadNextQuestion(themeName);
    }
  };

  const loadNextQuestion = async (themeName) => {
    const nextQuestion = await generateQuestion(themeName);
    if (nextQuestion) {
      setQuestionQueue(prev => [...prev, nextQuestion]);
    }
  };

  const handleAnswer = (selectedOption) => {
    if (isLoading) return;
    
    setSelectedAnswer(selectedOption);
    
    if (selectedOption === currentQuestion.answer) {
      setGameResult('win');
    } else {
      setGameResult('wrong');
    }
    
    setCurrentExplanation(currentQuestion.explanation || '');
    setShowModal(true);
  };

  const handleNextQuestion = () => {
    setShowModal(false);
    
    // Берем следующий вопрос из очереди или загружаем новый
    if (questionQueue.length > 0) {
      setCurrentQuestion(questionQueue[0]);
      setQuestionQueue(prev => prev.slice(1));
      
      // Если в очереди остался только 1 вопрос, загружаем следующий
      if (questionQueue.length <= 1) {
        const themeName = quizThemes.find(t => t.id === currentTheme).name;
        loadNextQuestion(themeName);
      }
    } else {
      // Если очередь пуста, загружаем новый вопрос
      const themeName = quizThemes.find(t => t.id === currentTheme).name;
      setIsLoading(true);
      generateQuestion(themeName).then(question => {
        if (question) {
          setCurrentQuestion(question);
        }
        setIsLoading(false);
      });
    }
  };

  const endGame = () => {
    setCurrentTheme(null);
    setCurrentQuestion(null);
    setShowModal(false);
    setQuestionQueue([]);
  };

  const getOptionClass = (option) => {
    if (!showModal) return 'option-button';
    if (option === currentQuestion.answer) {
      return 'option-button correct';
    }
    if (option === selectedAnswer && gameResult === 'wrong') {
      return 'option-button incorrect';
    }
    return 'option-button';
  };

  return (
    <div className="quiz-game-container">
      <button onClick={onExit} className="exit-button">
        ← Назад
      </button>

      {!currentTheme ? (
        <>
          <h2>Выберите тему викторины!</h2>
          <div className="theme-grid">
            {quizThemes.map((theme) => (
              <button
                key={theme.id}
                className="theme-button"
                onClick={() => handleThemeSelect(theme.id)}
                disabled={isLoading}
              >
                {theme.name}
              </button>
            ))}
          </div>
        </>
      ) : isLoading && !currentQuestion ? (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Загрузка первого вопроса...</p>
        </div>
      ) : (
        <>
          <h2>Тема: {quizThemes.find(t => t.id === currentTheme).name}</h2>
          
          <div className="question-container">
            <h3>{currentQuestion.text}</h3>
            <div className="options-grid">
              {currentQuestion.options.map((option, index) => (
                <button
                  key={index}
                  className={getOptionClass(option)}
                  onClick={() => !showModal && handleAnswer(option)}
                  disabled={showModal || isLoading}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          {isLoading && (
            <div className="loading-indicator">
              <p>Загрузка следующего вопроса...</p>
            </div>
          )}
        </>
      )}

      {showModal && (
        <GameModal 
          result={gameResult}
          onClose={handleNextQuestion}
          explanation={currentExplanation}
          onExit={endGame}
          reward={15}
        />
      )}
    </div>
  );
}