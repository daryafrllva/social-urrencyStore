export default function UserProfile({ account, balance, onDisconnect }) {
    const shortenAddress = (addr) => 
      `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  
    return (
      <div className="user-profile">
        <div>
          <p>{shortenAddress(account)}</p>
          <p>Balance: {balance} TOK</p>
        </div>
        <button onClick={onDisconnect}>Logout</button>
      </div>
    );
  }