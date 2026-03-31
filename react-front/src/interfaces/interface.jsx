import React, { useState } from 'react';
import './Game.css';
import Human from './humanVSHuman.jsx';
function App() {
  const [board, setBoard] = useState(Array(9).fill(0));
  const [isOver, setIsOver] = useState(false);
  const [winner, setWinner] = useState(null);
  const [winIndices, setWinIndices] = useState([]);
  const [isAiThinking, setIsAiThinking] = useState(false);
  
  // NOUVEAU : État pour choisir le mode (Minimax par défaut)
  const [aiMode, setAiMode] = useState('minimax'); // 'minimax' ou 'xgb'

  const handleClick = async (index) => {
    if (board[index] !== 0 || isOver || isAiThinking) return;

    // 1. Tour de l'Humain (X)
    const newBoard = [...board];
    newBoard[index] = 1;
    setBoard(newBoard);

    setIsAiThinking(true);

    // 2. Déterminer l'URL selon le mode choisi
    const endpoint = aiMode === 'minimax' ? "/play" : "/predict";

    try {
      console.log("Envoi au Backend :", { board: newBoard, endpoint });
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: newBoard })
      });
      const data = await response.json();
      console.log("Réponse du Backend :", data);
      // 3. Mise à jour du plateau avec le coup de l'IA (O)
      setBoard(data.best_board);
      
      if (data.is_over) {
        setWinner(data.winner);
        setWinIndices(data.win_indices || []);
        setIsOver(true);
      }
    } catch (e) {
      console.error("Erreur Backend", e);
    } finally {
      setIsAiThinking(false);
    }
  };

  const resetGame = () => {
    setBoard(Array(9).fill(0));
    setIsOver(false);
    setWinner(null);
    setWinIndices([]);
  };

  return (
    <div className='AllScreen'>
      <h1 className="title">TIC-TAC-TOE INTELLIGENT</h1>

      {/* --- LE SELECTEUR DE MODE (SWITCH) --- */}
      <div className="mode-selector">
        <button 
          className={`mode-btn ${aiMode === 'minimax' ? 'active' : ''}`}
          onClick={() => { setAiMode('minimax'); resetGame(); }}
        >
          Minimax (Alpha-Beta)
        </button>
        <button 
          className={`mode-btn ${aiMode === 'xgb' ? 'active' : ''}`}
          onClick={() => { setAiMode('xgb'); resetGame(); }}
        >
          Machine Learning (XGBoost)
        </button>
        <button 
          className={`mode-btn ${aiMode === 'human' ? 'active' : ''}`}
          onClick={() => { setAiMode('human'); resetGame(); }}
        >
          Human vs Human
        </button>
      </div>

      <div className='statusSection'>
        <div className='playerIntro'>
          <div className={`playerCase ${!isOver && !isAiThinking ? 'active-turn' : ''}`}><div className='userX'></div></div>
          <span className="vsText">VS</span>
          <div className={`playerCase ${isAiThinking ? 'thinking' : ''}`}><div className='userCircle'></div></div>
        </div>

        {isOver && (
          <div className="endGame">
            <h2 className={`winner-${winner}`}>{winner === 'Nul' ? "MATCH NUL" : `VICTOIRE DE ${winner}`}</h2>
            <button onClick={resetGame} className="mode-btn">REJOUER</button>
          </div>
        )}
      </div>
      
      {aiMode === 'human' ? (
        <div><Human/></div>
        
      ) : 
      <section id="gameContainer">
        {board.map((cell, i) => (
          <button 
            key={i} 
            onClick={() => handleClick(i)} 
            disabled={isOver || isAiThinking} 
            className={`case ${winIndices.includes(i) ? 'winLine' : ''}`}
          >
            <div className={cell === 1 ? "userX" : cell === -1 ? "userCircle" : ""}></div>
          </button>
        ))}
      </section>
      }
      
      
      <p className="mode-indicator">
        Mode actuel : <strong>{aiMode === 'minimax' ? 'Minimax' : aiMode === 'human' ? 'Humain vs Humain' : 'ML'}</strong>
      </p>
    </div>
  );
}

export default App;