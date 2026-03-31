import pandas as pd
import os

class NoeudMorpion:
    X = 1
    O = -1
    VIDE = 0

    def __init__(self, etat=None, tour=X):
        # initialisation du plateau (liste de 9 entiers)
        self.etat = etat if etat else [self.VIDE] * 9
        self.tour = tour
        self.best = None

    def __str__(self):
        """Affiche le plateau de manière lisible."""
        chars = {self.X: 'X', self.O: 'O', self.VIDE: ' '}
        res = ""
        for i in range(0, 9, 3):
            res += f"|{chars[self.etat[i]]}|{chars[self.etat[i+1]]}|{chars[self.etat[i+2]]}|\n"
        return res

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
        """Vérifie les victoires (100 pour X, -100 pour O, 0 sinon)."""
        victoires = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Horizontales
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Verticales
            [0, 4, 8], [2, 4, 6]             # Diagonales
        ]
        for v in victoires:
            if self.etat[v[0]] == self.etat[v[1]] == self.etat[v[2]] != self.VIDE:
                return self.etat[v[0]] * 100
        return 0

    def get_win_indices(self):
        """Retourne la liste des indices gagnants, ex: [0, 1, 2]"""
        victoires = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for v in victoires:
            if self.etat[v[0]] == self.etat[v[1]] == self.etat[v[2]] != self.VIDE:
                return v
        return []
    
    def is_terminal(self):
        return self.eval_heuristique() != 0 or self.VIDE not in self.etat

# --- ALGORITHME MINIMAX ---

def minimax(noeud, prof, alpha, beta, joueur_max):
    # Condition d'arrêt : profondeur maximale ou fin de partie
    if prof == 0 or noeud.is_terminal():
        return noeud.eval_heuristique()

    if noeud.tour == joueur_max:
        best_val = -float('inf')
        for fils in noeud.get_succ():
            val = minimax(fils, prof - 1, alpha, beta, joueur_max)
            if val > best_val:
                best_val = val
                noeud.best = fils
            
            # mise à jour de la borne Alpha
            alpha = max(alpha, best_val)
            
            # condition d'arret : si Max trouve une valeur supérieure à ce que Min acceptera
            if beta <= alpha:
                break 
        return best_val

    else:
        best_val = float('inf')
        for fils in noeud.get_succ():
            val = minimax(fils, prof - 1, alpha, beta, joueur_max)
            if val < best_val:
                best_val = val
                noeud.best = fils
            
            # mise à jour de la borne Bêta
            beta = min(beta, best_val)
            
            # condition d'arret Alpha : si Min trouve une valeur inférieure à ce que Max acceptera
            if beta <= alpha:
                break
        return best_val

# --- GÉNÉRATEUR DE DATASET ---

def generer_dataset():
    
    dataset = {}
    depart = NoeudMorpion()
    
    print("Analyse de tous les états possibles (Tour de X)...")
    
    def explorer(n):
        # ID unique : plateau + tour
        id_state = (tuple(n.etat), n.tour)
        if id_state in dataset:
            return
        
        # calcul du score Minimax
        score = minimax(n, 9,-float('inf'),float('inf'), NoeudMorpion.X)
        dataset[id_state] = score
        
        if not n.is_terminal():
            for fils in n.get_succ():
                explorer(fils)

    explorer(depart)
    
    # --- FILTRAGE ET ENCODAGE 
    rows = []
    for (etat, tour), score in dataset.items():
        if tour == NoeudMorpion.X:
            # 18 features (ci_x, ci_o)
            features_x = [1 if c == NoeudMorpion.X else 0 for c in etat]
            features_o = [1 if c == NoeudMorpion.O else 0 for c in etat]
            
            # Cibles
            x_wins = 1 if score > 0 else 0
            is_draw = 1 if score == 0 else 0
            
            rows.append(features_x + features_o + [x_wins, is_draw])

    # création des noms de colonnes
    cols = [f"c{i}_x" for i in range(9)] + [f"c{i}_o" for i in range(9)] + ["x_wins", "is_draw"]
    
    # export via Pandas
    df = pd.DataFrame(rows, columns=cols)
    
    if not os.path.exists('ressources'):
        os.makedirs('ressources')
        
    df.to_csv('back/csv/dataset.csv', index=False)
    print(f"Succès ! {len(df)} états enregistrés dans back/csv/dataset.csv")

def jouer():
    jeu = NoeudMorpion()
    print("=== TEST IA MINIMAX (Profondeur 9) ===")
    print("Légende des positions :")
    print("|0|1|2|\n|3|4|5|\n|6|7|8|\n")
    print("Tu es X (1), l'IA est O (-1).")

    while not jeu.is_terminal():
        print("\nPlateau actuel :")
        print(jeu)

        if jeu.tour == NoeudMorpion.X:
            # Tour de l'humain (Nathalie)
            try:
                choix = int(input("Choisis une case (0-8) : "))
                if 0 <= choix <= 8 and jeu.etat[choix] == NoeudMorpion.VIDE:
                    jeu = jeu.play(choix)
                else:
                    print("Case invalide ou déjà occupée !")
            except ValueError:
                print("Entrée invalide ! Tape un chiffre entre 0 et 8.")
        else:
            # Tour de l'IA
            print("L'IA réfléchit...")
            # On cherche à maximiser pour l'IA (ici on passe -1 car c'est le tour de O)
            # Pour simplifier le test, on utilise l'algorithme minimax existant
            minimax(jeu, 9, -float('inf'), float('inf'), 1)
            if jeu.best:
                jeu = jeu.best
                print(f"L'IA a joué en position.")
            else:
                # Sécurité si aucun coup n'est trouvé
                for i in range(9):
                    if jeu.etat[i] == NoeudMorpion.VIDE:
                        jeu = jeu.play(i)
                        break

    print("\n=== FIN DE PARTIE ===")
    print(jeu)
    score_final = jeu.eval_heuristique()
    if score_final > 0:
        print("Bravo, tu as gagné !")
    elif score_final < 0:
        print("L'IA a gagné !")
    else:
        print("Match nul !")

if __name__ == "__main__":
    jouer()
# if __name__ == "__main__":
#     generer_dataset()