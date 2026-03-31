from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from Minimax import NoeudMorpion, minimax 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState(BaseModel):
    board: List[int]

@app.post("/play")
def get_move(state: GameState):
    # 1. Créer le nœud actuel
    noeud = NoeudMorpion(etat=state.board, tour=-1) # Tour de l'IA (O)
    
    # 2. Calculer le meilleur coup
    minimax(noeud, 8, -float('inf'), float('inf'), 1)
    
    # 3. Déterminer l'état après le coup de l'IA
    noeud_final = noeud.best if noeud.best else noeud
    score = noeud_final.eval_heuristique()
    termine = noeud_final.is_terminal()
    
    gagnant = None
    if score > 0: gagnant = "X"
    elif score < 0: gagnant = "O"
    elif termine: gagnant = "Nul"

    return {
        "best_board": noeud_final.etat,
        "winner": gagnant,
        "is_over": termine
    }
    
# humain vs humain
@app.post("/check")
def check_game(state: GameState):
    # On crée le noeud pour utiliser ses méthodes de vérification
    noeud = NoeudMorpion(etat=state.board)
    
    score = noeud.eval_heuristique()
    termine = noeud.is_terminal()
    indices_gagnants = noeud.get_win_indices()
    
    gagnant = "X" if score > 0 else "O" if score < 0 else ("Nul" if termine else None)
    
    return {
        "winner": gagnant,
        "win_indices": indices_gagnants,
        "is_over": termine
    }