import React, { useState } from 'react';

function App() {
  const [board, setBoard] = useState(Array(9).fill(0));
  const [winner, setWinner] = useState(null); // Stocke 'X', 'O' ou 'Nul'
  const [isOver, setIsOver] = useState(false); // Bloque le jeu à la fin

  const handleClick = async (index) => {
    // Empêche de jouer si la case est prise ou si la partie est finie
    if (board[index] !== 0 || isOver) return;

    // 1. Le joueur (X) joue
    const newBoard = [...board];
    newBoard[index] = 1;
    setBoard(newBoard);

    try {
      // 2. Appel à l'IA Python
      const response = await fetch("http://127.0.0.1:8000/play", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: newBoard })
      });
      
      const data = await response.json();
      
      // 3. Mise à jour des états avec les données du backend
      setBoard(data.best_board);
      setWinner(data.winner);   // 'X', 'O' ou 'Nul'
      setIsOver(data.is_over);  // true ou false
    } catch (error) {
      console.error("Erreur de connexion au backend:", error);
    }
  };

  const resetGame = () => {
    setBoard(Array(9).fill(0));
    setWinner(null);
    setIsOver(false);
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Morpion IA</h1>

      {/* Affichage du résultat */}
      {winner && (
        <div style={{ marginBottom: '20px' }}>
          <h2 style={{ color: winner === 'X' ? '#28a745' : winner === 'O' ? '#dc3545' : '#ffc107' }}>
            {winner === 'Nul' ? "Match Nul !" : `Le gagnant est : ${winner}`}
          </h2>
          <button onClick={resetGame} style={styles.resetBtn}>
            Nouvelle Partie
          </button>
        </div>
      )}

      {/* Grille de jeu */}
      <div style={styles.grid}>
        {board.map((cell, i) => (
          <button 
            key={i} 
            onClick={() => handleClick(i)}
            disabled={isOver || cell !== 0}
            style={{
              ...styles.cell,
              cursor: isOver || cell !== 0 ? 'not-allowed' : 'pointer',
              color: cell === 1 ? '#007bff' : '#dc3545'
            }}
          >
            {cell === 1 ? 'X' : cell === -1 ? 'O' : ''}
          </button>
        ))}
      </div>
    </div>
  );
}

// Styles simples pour l'affichage
const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 100px)',
    gap: '10px',
    justifyContent: 'center'
  },
  cell: {
    width: '100px',
    height: '100px',
    fontSize: '32px',
    fontWeight: 'bold',
    backgroundColor: '#fff',
    border: '2px solid #333',
    borderRadius: '8px'
  },
  resetBtn: {
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    backgroundColor: '#333',
    color: '#fff',
    border: 'none',
    borderRadius: '5px'
  }
};

export default App;