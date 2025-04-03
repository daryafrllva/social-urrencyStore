// eslint-disable-next-line no-unused-vars
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

const quizQuestions = {
  1: [
    {
      text: "Какое животное считается национальным символом Австралии?",
      options: ["Кенгуру", "Коала", "Вомбат", "Ехидна"],
      answer: "Кенгуру",
      explanation: "Кенгуру является национальным символом Австралии и изображен на гербе страны."
    },
    {
      text: "Какое млекопитающее умеет летать?",
      options: ["Пингвин", "Летучая мышь", "Кенгуру", "Дельфин"],
      answer: "Летучая мышь",
      explanation: "Летучие мыши - единственные млекопитающие, способные к активному полету."
    }
  ],
  2: [
    {
      text: "Какой газ преобладает в атмосфере Земли?",
      options: ["Кислород", "Азот", "Углекислый газ", "Водород"],
      answer: "Азот",
      explanation: "Атмосфера Земли состоит примерно на 78% из азота."
    }
  ]
};

export default function QuizGame({ onExit }) {
  const [currentTheme, setCurrentTheme] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [currentExplanation, setCurrentExplanation] = useState('');

  const handleThemeSelect = (themeId) => {
    setCurrentTheme(themeId);
    setCurrentQuestion(0);
    setScore(0);
  };

  const handleAnswer = (selectedOption) => {
    const currentQuiz = quizQuestions[currentTheme][currentQuestion];
    setSelectedAnswer(selectedOption);
    
    if (selectedOption === currentQuiz.answer) {
      setScore(score + 1);
      setGameResult('win');
    } else {
      setGameResult('wrong');
    }
    
    setCurrentExplanation(currentQuiz.explanation || '');
    setShowModal(true);
  };

  const handleNextQuestion = () => {
    setShowModal(false);
    if (currentQuestion < quizQuestions[currentTheme].length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Игра завершена
      endGame();
    }
  };

  const endGame = () => {
    setCurrentTheme(null);
    setCurrentQuestion(0);
    setShowModal(false);
  };

  const getOptionClass = (option) => {
    if (!showModal) return 'option-button';
    if (option === quizQuestions[currentTheme][currentQuestion].answer) {
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
              >
                {theme.name}
              </button>
            ))}
          </div>
        </>
      ) : (
        <>
          <div className="progress-container">
            <div className="progress-text">
              Вопрос {currentQuestion + 1} из {quizQuestions[currentTheme].length}
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{
                  width: `${((currentQuestion + 1) / quizQuestions[currentTheme].length) * 100}%`
                }}
              ></div>
            </div>
          </div>

          <h2>Тема: {quizThemes.find(t => t.id === currentTheme).name}</h2>
          <div className="score-display">Счет: {score}</div>
          
          <div className="question-container">
            <h3>{quizQuestions[currentTheme][currentQuestion].text}</h3>
            <div className="options-grid">
              {quizQuestions[currentTheme][currentQuestion].options.map((option, index) => (
                <button
                  key={index}
                  className={getOptionClass(option)}
                  onClick={() => !showModal && handleAnswer(option)}
                  disabled={showModal}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {showModal && (
        <GameModal 
          result={gameResult}
          onClose={handleNextQuestion}
          explanation={currentExplanation}
          isFinalQuestion={currentQuestion === quizQuestions[currentTheme].length - 1}
          onExit={endGame}
        />
      )}
    </div>
  );
}