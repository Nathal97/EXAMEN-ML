import numpy as np

class NoeudMorpion:
    X = 1
    O = -1
    VIDE = 0

    def __init__(self, etat=None, tour=X):
        self.etat = etat if etat else [self.VIDE] * 9
        self.tour = tour
        self.best = None

    def play(self, position):
        nouvel_etat = list(self.etat)
        nouvel_etat[position] = self.tour
        return NoeudMorpion(nouvel_etat, -self.tour)

    def get_succ(self):
        successeurs = []
        for i in range(9):
            if self.etat[i] == self.VIDE:
                successeurs.append(self.play(i))
        return successeurs

    def eval_heuristique(self):
        """Vérifie les victoires réelles (100 pour X, -100 pour O)."""
        victoires = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for v in victoires:
            if self.etat[v[0]] == self.etat[v[1]] == self.etat[v[2]] != self.VIDE:
                return self.etat[v[0]] * 100
        return 0
    
    def get_win_indices(self):
        victoires = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        for v in victoires:
            if self.etat[v[0]] == self.etat[v[1]] == self.etat[v[2]] != self.VIDE:
                return v
        return []
    
    def is_terminal(self):
        return self.eval_heuristique() != 0 or self.VIDE not in self.etat

# --- FONCTION D'ÉVALUATION PAR MACHINE LEARNING ---

def evaluer_avec_ml(noeud, model_win, model_draw):
    """
    Utilise XGBoost pour 'deviner' la valeur d'un plateau non terminé.
    """
    # Préparation des 18 features pour le modèle (X et O séparés)
    features_x = [1 if c == 1 else 0 for c in noeud.etat]
    features_o = [1 if c == -1 else 0 for c in noeud.etat]
    X_input = np.array(features_x + features_o).reshape(1, -1)
    
    # Récupération des probabilités (classe 1 = True)
    prob_win_x = model_win.predict_proba(X_input)[0][1]   # Proba que X gagne
    prob_draw = model_draw.predict_proba(X_input)[0][1]    # Proba nul
    
    # Calcul du score hybride :
    # X veut maximiser (proche de 100), O veut minimiser (proche de -100)
    # Si prob_win_x est forte -> score positif. 
    # Si prob_win_x est faible et prob_draw forte -> score proche de 0.
    score = (prob_win_x * 100) + (prob_draw * 10)
    
    # Si c'est l'IA (O) qui évalue, on ajuste la perspective si nécessaire, 
    # mais Minimax s'en occupe avec joueur_max.
    return score

# --- ALGORITHME MINIMAX HYBRIDE ---

def minimax_hybride(noeud, prof, alpha, beta, joueur_max, model_win, model_draw):
    """
    Minimax avec élagage Alpha-Bêta et évaluation ML à profondeur fixe.
    """
    # 1. CAS TERMINAL : Quelqu'un a gagné ou match nul réel
    if noeud.is_terminal():
        return noeud.eval_heuristique()

    # 2. CAS HYBRIDE : Profondeur atteinte mais jeu en cours
    if prof == 0:
        # On utilise l'IA statistique pour estimer la valeur du plateau
        return evaluer_avec_ml(noeud, model_win, model_draw)

    # 3. LOGIQUE MINIMAX CLASSIQUE
    if noeud.tour == joueur_max:
        best_val = -float('inf')
        for fils in noeud.get_succ():
            val = minimax_hybride(fils, prof - 1, alpha, beta, joueur_max, model_win, model_draw)
            if val > best_val:
                best_val = val
                noeud.best = fils
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break 
        return best_val
    else:
        best_val = float('inf')
        for fils in noeud.get_succ():
            val = minimax_hybride(fils, prof - 1, alpha, beta, joueur_max, model_win, model_draw)
            if val < best_val:
                best_val = val
                noeud.best = fils
            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val