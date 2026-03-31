
# Installation et Configuration

## 1. Prérequis
    Python 3.10 ou supérieur

    Un accès internet pour la première installation des dépendances

## 2. Création de l'environnement virtuel (venv)
Il est conseillé d'utiliser un seul environnement virtuel à la racine pour économiser l'espace disque (partagé entre le dossier IA et le Backend).

- Lancez une de ces suites de commandes selon vôtre **OS**: 

**Sur Linux**:
```Bash
python3 -m venv .venv
source .venv/bin/activate
```
**Sur Windows**:
```Bash
python3 -m venv .venv
.venv\Scripts\activate
```
## 3. Installation des dépendances
Une fois l'environnement **activé**, installez les packages nécessaires :

- Installer les packages pour **fastAPI**
```Bash
pip install --upgrade pip
pip install -r requirements.txt
```


## 4. Lancer le back

```Bash
uvicorn main:app --reload
```

## 5. Lancer le front

```Bash
cd react-front
npm install
npm run dev
```