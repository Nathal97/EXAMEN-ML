import React, { useState } from 'react';
import './Game.css'

function Human() {
  const [board, setBoard] = useState(Array(9).fill(0));
  const [currentPlayer, setCurrentPlayer] = useState(1); // 1 pour X, -1 pour O
  const [winner, setWinner] = useState(null);
  const [winIndices, setWinIndices] = useState([]);
  const [isOver, setIsOver] = useState(false);

  const handleClick = async (index) => {
    if (board[index] !== 0 || isOver) return;

    // 1. Marquer la case selon le joueur actuel
    const newBoard = [...board];
    newBoard[index] = currentPlayer;
    setBoard(newBoard);

    try {
      // 2. Demander au Backend si la partie est finie
      const response = await fetch("http://127.0.0.1:8000/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: newBoard })
      });
      const data = await response.json();
      
      if (data.is_over) {
        setWinner(data.winner);
        setWinIndices(data.win_indices || []);
        setIsOver(true);
      } else {
        // 3. Changer de joueur si la partie continue
        setCurrentPlayer(currentPlayer === 1 ? -1 : 1);
      }
    } catch (e) { console.error("Erreur Backend", e); }
  };

  return (
    <div className='AllScreen'>
      {/* <h1>Morpion : Humain vs Humain</h1> */}
      {!isOver ? (
        <h3>Tour du joueur : <span style={{ color: currentPlayer === 1 ? 'blue' : 'red' }}>
          {currentPlayer === 1 ? 'X' : 'O'}
        </span></h3>
      ) : (
        <div>
          <h2 style={{ color: winner === 'X' ? 'green' : winner === 'O' ? 'red' : 'orange' }}>
            {winner === 'Nul' ? "Match Nul !" : `Victoire de ${winner} !`}
          </h2>
          <button onClick={() => window.location.reload()} style={btnStyle}>Rejouer</button>
        </div>
      )}

      <section id="gameContainer">
        {board.map((cell, i) => (
          <button 
            key={i} 
            onClick={() => handleClick(i)} 
            disabled={isOver} 
            className={`case`}
          >
            <div className={cell === 1 ? "userX" : cell === -1 ? "userCircle" : ""}>
            </div>
          </button>
        ))}
      </section>
    </div>
  );
}
// style={{ ...cellStyle, 
            //   backgroundColor: winIndices.includes(i) ? (winner === 'X' ? '#d4edda' : '#f8d7da') : '#fff',
            //   color: cell === 1 ? 'blue' : cell === -1 ? 'red' : 'transparent'
            // }}>
// Mêmes styles que précédemment

const btnStyle = { padding: '10px 20px', cursor: 'pointer', borderRadius: '5px', backgroundColor: '#333', color: '#fff' };

export default Human;