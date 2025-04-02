import { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import ConnectWallet from './components/auth/ConnectWallet';
import UserProfile from './components/auth/UserProfile';
import GameControls from './components/game/GameControls';
import GameResult from './components/game/GameResult';
import PrizeModal from './components/game/PrizeModal';
import './styles/game.css';

// Конфигурация контракта (замените на свои значе
const CONTRACT_ADDRESS = "0x123..."; // Адрес вашего контракта
const CONTRACT_ABI = [ /* Вставьте ABI вашего контракта */ ];

function App() {
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [account, setAccount] = useState(null);
  const [contract, setContract] = useState(null);
  const [tokenBalance, setTokenBalance] = useState("0");
  const [result, setResult] = useState(null);
  const [showPrize, setShowPrize] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [prizeClaimed, setPrizeClaimed] = useState(false);

  // Подключение кошелька
  const connectWallet = async () => {
    if (window.ethereum) {
      try {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const accounts = await provider.send("eth_requestAccounts", []);
        const signer = provider.getSigner();
        const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);
        
        setProvider(provider);
        setSigner(signer);
        setAccount(accounts[0]);
        setContract(contract);
        
        updateTokenBalance();
      } catch (error) {
        console.error("Error connecting wallet:", error);
      }
    } else {
      alert("Please install MetaMask!");
    }
  };

  // Обновление баланса токенов
  const updateTokenBalance = async () => {
    if (contract && account) {
      const balance = await contract.balanceOf(account);
      setTokenBalance(ethers.utils.formatUnits(balance, 18));
    }
  };

  // Обработка выбора игрока
  const handleChoice = (playerChoice) => {
    const choices = ['Rock', 'Paper', 'Scissors'];
    const computerChoice = choices[Math.floor(Math.random() * choices.length)];
    const gameResult = determineWinner(playerChoice, computerChoice);
    
    setResult({ playerChoice, computerChoice, gameResult });
    setShowPrize(gameResult === 'Win');
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
  };

  // Запрос награды
  const claimPrize = async () => {
    try {
      const tx = await contract.claimTo(account, ethers.utils.parseUnits("10", 18));
      await tx.wait();
      setPrizeClaimed(true);
      updateTokenBalance();
      setShowModal(false);
      alert('Prize claimed successfully!');
    } catch (error) {
      console.error("Error claiming prize:", error);
      alert('Failed to claim prize: ' + error.message);
    }
  };

  // Слушатель изменения аккаунта
  useEffect(() => {
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        setAccount(accounts[0] || null);
        if (accounts[0]) updateTokenBalance();
      });
    }
  }, []);

  return (
    <div className="game-container">
      {!account ? (
        <ConnectWallet onConnect={connectWallet} />
      ) : (
        <>
          <UserProfile 
            account={account} 
            balance={tokenBalance}
            onDisconnect={() => {
              setAccount(null);
              setProvider(null);
              setSigner(null);
            }}
          />

          {!result ? (
            <GameControls onChoice={handleChoice} />
          ) : (
            <GameResult 
              result={result} 
              onReset={resetGame}
              showPrize={showPrize && !prizeClaimed}
              onClaimPrize={() => setShowModal(true)}
            />
          )}

          {showModal && (
            <PrizeModal
              onClose={() => setShowModal(false)}
              onConfirm={claimPrize}
              loading={false}
            />
          )}
        </>
      )}
    </div>
  );
}

export default App;