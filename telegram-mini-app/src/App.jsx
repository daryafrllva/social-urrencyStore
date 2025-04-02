import { useState, useEffect } from 'react';
// import { WebApp } from '@twa-dev/sdk'; // Закомментировано для работы в вебе
import UserProfile from "../components/auth/UserProfile";
import "../styles/game.css";
import "../components/game/RockPaperScissors";

export default function RockPaperScissors() {
  const [account, setAccount] = useState(null);
  const [tokenBalance, setTokenBalance] = useState("0");
  const [result, setResult] = useState(null);
  const [showPrize, setShowPrize] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [prizeClaimed, setPrizeClaimed] = useState(false);

  // Инициализация Telegram WebApp - закомментировано для веба
  useEffect(() => {
    // WebApp.ready(); // Закомментировано для веба
    // WebApp.expand(); // Закомментировано для веба

    // Получаем данные пользователя из Telegram - заменим на заглушку для веба
    // if (WebApp.initDataUnsafe?.user) {
    //   const tgUser = WebApp.initDataUnsafe.user;
    //   setAccount({
    //     address: tgUser.id.toString(),
    //     username: tgUser.username || `user_${tgUser.id}`
    //   });
    // }

    // Для веба временно создадим фейковые данные пользователя
    setAccount({
      address: 'demo', // Заглушка для адреса
      username: 'demo_user' // Заглушка для имени пользователя
    });

  }, []);

  // Обработка выбора игрока
  const handleChoice = (playerChoice) => {
    const choices = ['Rock', 'Paper', 'Scissors'];
    const computerChoice = choices[Math.floor(Math.random() * choices.length)];
    const gameResult = determineWinner(playerChoice, computerChoice);
    
    setResult({ playerChoice, computerChoice, gameResult });
    setShowPrize(gameResult === 'Win');

    // Для веба, просто убираем все, что связано с кнопками Telegram
    // В реальном вебе нужно будет добавить кнопку вручную, если это необходимо
  };

  // Определение победителя
  const determineWinner = (playerChoice, computerChoice) => {
    if (playerChoice === computerChoice) return 'Tie';
    if (
      (playerChoice === 'Rock' && computerChoice === 'Scissors') ||
      (playerChoice === 'Paper' && computerChoice === 'Rock') ||
      (playerChoice === 'Scissors' && computerChoice === 'Paper')
    ) {
      return 'Win';
    }
    return 'Lose';
  };

  // Сброс игры
  const resetGame = () => {
    setResult(null);
    setShowPrize(false);
    setPrizeClaimed(false);
    // Закомментируем любые действия с Telegram
    // WebApp.MainButton.hide(); // Закомментировано для веба
  };

  // Запрос награды
  const claimPrize = () => {
    setShowModal(true);
    // Закомментируем любые действия с Telegram
    // WebApp.MainButton.hide(); // Закомментировано для веба
  };

  // Подтверждение получения награды
  const confirmClaim = () => {
    setPrizeClaimed(true);
    setTokenBalance(prev => (parseFloat(prev) + 10).toString());
    setShowModal(false);

    // Для веба можно оставить этот вызов или просто убрать
    // WebApp.sendData(JSON.stringify({
    //   action: 'prize_claimed',
    //   amount: 10,
    //   userId: WebApp.initDataUnsafe.user.id
    // })); // Закомментировано для веба
  };

  return (
    <div className="game-container">
      {!account ? (
        <ConnectWallet onConnect={() => setAccount({ address: 'demo', username: 'demo' })} />
      ) : (
        <>
          <UserProfile 
            account={account} 
            balance={tokenBalance}
            onDisconnect={() => setAccount(null)} // Убираем WebApp.close() для веба
          />

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
        </>
      )}
    </div>
  );
}
