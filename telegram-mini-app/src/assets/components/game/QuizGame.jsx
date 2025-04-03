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

export default function QuizGame({ onExit, onWin }) {
  const [currentTheme, setCurrentTheme] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [tgReady, setTgReady] = useState(false);

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.expand();
      setTgReady(true);
    }
  }, []);

  const handleThemeSelect = (themeId) => {
    setCurrentTheme(themeId);
    setCurrentQuestion(0);
    setScore(0);
  };

  const handleAnswer = (selectedOption) => {
    const currentQuiz = quizQuestions[currentTheme][currentQuestion];
    setSelectedAnswer(selectedOption);
    
    const isCorrect = selectedOption === currentQuiz.answer;
    setGameResult(isCorrect ? 'win' : 'wrong');
    
    if (isCorrect) {
      const newScore = score + 1;
      setScore(newScore);
      
      // Начисляем монеты за каждый правильный ответ
      const themeReward = quizThemes.find(t => t.id === currentTheme).reward;
      onWin(themeReward);
    }
    
    setShowModal(true);
  };

  const handleNext = () => {
    setShowModal(false);
    if (currentQuestion < quizQuestions[currentTheme].length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      endGame();
    }
  };

  const endGame = () => {
    // Отправляем финальный результат в Telegram
    if (window.Telegram?.WebApp && score > 0) {
      const totalReward = score * quizThemes.find(t => t.id === currentTheme).reward;
      window.Telegram.WebApp.sendData(JSON.stringify({
        action: 'quiz_completed',
        score: score,
        reward: totalReward,
        theme: quizThemes.find(t => t.id === currentTheme).name
      }));
    }
    
    setCurrentTheme(null);
    setCurrentQuestion(0);
    setShowModal(false);
  };

  const getOptionClass = (option) => {
    if (!showModal) return 'option-button';
    const isCorrect = option === quizQuestions[currentTheme][currentQuestion].answer;
    return `option-button ${isCorrect ? 'correct' : option === selectedAnswer ? 'incorrect' : ''}`;
  };

  return (
    <div className="quiz-game-container">
      {tgReady && (
        <button 
          onClick={() => window.Telegram?.WebApp?.close()}
          className="tg-close-btn"
        >
          Закрыть игру
        </button>
      )}
      
      <button onClick={onExit} className="exit-button">
        ← Назад
      </button>

      {!currentTheme ? (
        <div className="theme-selection">
          <h2>Выберите тему викторины</h2>
          <div className="theme-grid">
            {quizThemes.map(theme => (
              <button
                key={theme.id}
                className="theme-button"
                onClick={() => handleThemeSelect(theme.id)}
              >
                {theme.name}
                <span className="reward-badge">+{theme.reward} монет/вопрос</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="quiz-content">
          <div className="quiz-header">
            <span className="theme-name">{quizThemes.find(t => t.id === currentTheme).name}</span>
            <span className="score">Счет: {score}</span>
          </div>
          
          <div className="progress">
            Прогресс: {currentQuestion + 1}/{quizQuestions[currentTheme].length}
          </div>
          
          <div className="question">
            <h3>{quizQuestions[currentTheme][currentQuestion].text}</h3>
            <div className="options">
              {quizQuestions[currentTheme][currentQuestion].options.map((option, i) => (
                <button
                  key={i}
                  className={getOptionClass(option)}
                  onClick={() => !showModal && handleAnswer(option)}
                  disabled={showModal}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <GameModal 
          result={gameResult}
          onClose={gameResult === 'win' ? handleNext : endGame}
          explanation={quizQuestions[currentTheme][currentQuestion].explanation}
          reward={gameResult === 'win' ? quizThemes.find(t => t.id === currentTheme).reward : 0}
        />
      )}
    </div>
  );
}