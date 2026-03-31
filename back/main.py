import joblib
import numpy as np
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from Minimax import NoeudMorpion, minimax_hybride

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

# Récupère le dossier où se trouve main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construit le chemin vers le dossier models
MODEL_WIN_PATH = os.path.join(BASE_DIR, "models", "xgb_xwins.joblib")
MODEL_DRAW_PATH = os.path.join(BASE_DIR, "models", "xgb_draw.joblib")

print(f"Recherche du modèle ici : {MODEL_WIN_PATH}") # Pour vérifier dans le terminal
print(f"Recherche du modèle ici : {MODEL_DRAW_PATH}") # Pour vérifier dans le terminal

model_win = None
model_draw = None

if os.path.exists(MODEL_WIN_PATH) and os.path.exists(MODEL_DRAW_PATH):
    model_win = joblib.load(MODEL_WIN_PATH)
    model_draw = joblib.load(MODEL_DRAW_PATH)
    print("Modèles XGB_WIN et XGB_DRAW chargés.")
else:
    print("Modèles .joblib manquants dans back/models/")

def prepare_features(board):
    """Transforme le board [9] en 18 features (X et O séparés) pour le ML."""
    features_x = [1 if c == 1 else 0 for c in board]
    features_o = [1 if c == -1 else 0 for c in board]
    return np.array(features_x + features_o).reshape(1, -1)

class GameState(BaseModel):
    board: List[int]

@app.post("/play")
def play_endpoint(state: GameState):
    # 1. Vérifier si l'humain a déjà gagné
    noeud_init = NoeudMorpion(etat=state.board)
    if noeud_init.is_terminal():
        score = noeud_init.eval_heuristique()
        return {
            "best_board": state.board,
            "winner": "X" if score > 0 else "Nul",
            "win_indices": noeud_init.get_win_indices(),
            "is_over": True
        }

    # 2. Lancer l'IA Hybride (O joue, donc cherche à minimiser)
    noeud_racine = NoeudMorpion(etat=state.board, tour=-1)
    minimax_hybride(noeud_racine, 3, -float('inf'), float('inf'), 1, model_win, model_draw)
    
    noeud_ia = noeud_racine.best if noeud_racine.best else noeud_racine
    score_f = noeud_ia.eval_heuristique()
    termine_f = noeud_ia.is_terminal()
    
    gagnant = "O" if score_f < 0 else ("X" if score_f > 0 else ("Nul" if termine_f else None))

    return {
        "best_board": noeud_ia.etat,
        "winner": gagnant,
        "win_indices": noeud_ia.get_win_indices(),
        "is_over": termine_f
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
    
@app.post("/predict")
def predict_move_ml(state: GameState):
    if model_win is None or model_draw is None:
        return {"error": "Modèles ML non disponibles"}

    board = state.board
    best_move = -1
    max_score = -float('inf')

    # L'IA teste chaque case vide (0)
    for i in range(9):
        if board[i] == 0:
            temp_board = list(board)
            temp_board[i] = -1 # Simulation du coup de l'IA (O)
            features = prepare_features(temp_board)
            
            # On récupère les probabilités des deux modèles
            # proba[0][1] car l'index 1 est la probabilité de la classe positive (Win/Draw)
            prob_win = model_win.predict_proba(features)[0][1]
            prob_draw = model_draw.predict_proba(features)[0][1]
            
            # Score combiné : On favorise la victoire, mais on accepte le nul
            score_combinaison = (prob_win * 2.0) + prob_draw 

            if score_combinaison > max_score:
                max_score = score_combinaison
                best_move = i

    # Appliquer le coup choisi par le ML
    final_board = list(board)
    if best_move != -1:
        final_board[best_move] = -1

    # Calcul de l'état final via la logique du Noeud
    noeud_final = NoeudMorpion(etat=final_board)
    score_final = noeud_final.eval_heuristique()
    termine = noeud_final.is_terminal()
    gagnant = None
    if score_final > 0: gagnant = "X"
    elif score_final < 0: gagnant = "O"
    elif termine: gagnant = "Nul"

    return {
        "best_board": final_board,
        "winner": gagnant,
        "win_indices": noeud_final.get_win_indices(),
        "is_over": termine
    }
