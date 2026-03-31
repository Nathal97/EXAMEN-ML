import React, { useState } from 'react';

function App() {
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
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Morpion : Humain vs Humain</h1>
      
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

      <div style={gridStyle}>
        {board.map((cell, i) => (
          <button key={i} onClick={() => handleClick(i)} disabled={isOver}
            style={{ ...cellStyle, 
              backgroundColor: winIndices.includes(i) ? (winner === 'X' ? '#d4edda' : '#f8d7da') : '#fff',
              color: cell === 1 ? 'blue' : cell === -1 ? 'red' : 'transparent'
            }}>
            {cell === 1 ? 'X' : cell === -1 ? 'O' : ''}
          </button>
        ))}
      </div>
    </div>
  );
}

// Mêmes styles que précédemment
const gridStyle = { display: 'grid', gridTemplateColumns: 'repeat(3, 100px)', gap: '10px', justifyContent: 'center', marginTop: '20px' };
const cellStyle = { width: '100px', height: '100px', fontSize: '32px', fontWeight: 'bold', border: '2px solid #333', borderRadius: '8px', cursor: 'pointer' };
const btnStyle = { padding: '10px 20px', cursor: 'pointer', borderRadius: '5px', backgroundColor: '#333', color: '#fff' };

export default App;