# PA-Explorer

API REST Python/FastAPI pour interagir avec IBM Planning Analytics SaaS.

## Prérequis

- Python 3.11+
- pip

test:

```bash
   python --version 
   # exemple : Python 3.12.13 
```

## Installation

```bash
# 1. Cloner le dépôt
git clone <repo-url>
cd pa-explorer

# 2. Créer et activer un environnement virtuel
python3.12 -m venv venv (recommended version)
python -m venv .venv 
or
python3 -m venv venv 

source .venv/bin/activate        # Linux/macOS
.\venv\Scripts\activate  

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env.local
# Éditer .env.local et renseigner les valeurs IBM_PA_TENANT_ID et IBM_PA_API_KEY
```

## Lancement

```bash
uvicorn app.main:app --reload
```

```powershell
 python -m uvicorn app.main:app --reload
```

L'API est disponible sur `http://localhost:8000`.  
La documentation interactive Swagger est accessible sur `http://localhost:8000/docs`.

## Tester les endpoints d'authentification

### POST /auth/request — Demander un magic link

1. Ouvre Swagger : http://localhost:8000/docs
2. Trouve l'endpoint POST /api/v1/auth/request
3. Remplis le Request body avec tes vraies valeurs :

```json
{
  "email": "smalho@aexis.com",
  "ibm_pa_version": "V12",
  "credentials_payload": {
    "tenant_id": "ta-valeur-depuis-.env.local",
    "api_key": "ta-valeur-depuis-.env.local"
  }
}
```.
4. Clique Execute. Tu dois obtenir un 200 avec un message générique.
5. Regarde la console uvicorn pour voir le magic link loggé :

INFO: Magic link emis pour smalho@aexis.com : http://localhost:8000/api/v1/auth/verify?token=...

### GET /auth/verify — Utiliser le magic link

1. Copie le token complet en lançant le script utilitaire :

```powershell
python scripts/get_magic_link_token.py
```

Cela affiche le token récent, son email et l'URL complète de vérification
2. Va à http://localhost:8000/api/v1/auth/verify?token=COLLE_TON_TOKEN_ICI
   Ou utilise Swagger avec GET /api/v1/auth/verify en passant le token en query param.
3. Tu dois obtenir un 200 "Session créée. Vous êtes authentifié." et un cookie session_token posé.

## Procédures de développement

### Lancer les tests automatisés

Les tests pytest utilisent une base SQLite en mémoire isolée par test.
Les fixtures communes sont séparées par domaine sous `tests/fixtures/`
et chargées par `tests/conftest.py`.

```bash
venv/bin/python -m pytest -q
```

### Premier démarrage

1. Activer le venv : `.\venv\Scripts\activate` (PowerShell) ou `source venv/bin/activate` (macOS/Linux)
2. Installer les dépendances : `pip install -r requirements.txt`
3. Copier `.env.example` vers `.env.local` et renseigner les valeurs
4. Migrer le schéma : `venv/bin/alembic upgrade head`
5. Peupler les données initiales : `python scripts/seed_db.py`
6. Lancer le serveur : `python -m uvicorn app.main:app --reload`
7. Ouvrir Swagger : http://localhost:8000/docs

### Diagnostiquer l'état de la base

Pour vérifier rapidement l'état de la base SQLite, exécuter le script 
de diagnostic.

```bash
python scripts/check_db.py
```

Le script liste toutes les tables présentes et le nombre de lignes 
par table. Il affiche aussi le contenu des tables de référence comme 
user_allowlist.

Pour vérifier la revision Alembic appliquée :

```bash
venv/bin/alembic current
```

### Réinitialiser la base

1. Arrêter uvicorn avec Ctrl+C
2. Supprimer la base : `del pa_explorer.db` (Windows) ou `rm pa_explorer.db` (macOS/Linux)
3. Réappliquer les migrations : `venv/bin/alembic upgrade head`
4. Repeupler les données initiales : `python scripts/seed_db.py`
5. Relancer le serveur : `python -m uvicorn app.main:app --reload`

### En cas de fichier verrouillé

Si la suppression échoue avec un message "fichier en cours d'utilisation":

1. Lister les processus Python : `Get-Process | Where-Object {$_.ProcessName -like "*python*"}`
2. Tuer les instances : `Get-Process python3.12 | Stop-Process -Force`
3. Réessayer la suppression

## Gestion de la clé de chiffrement Fernet

PA-Explorer chiffre les credentials IBM PA des utilisateurs avec Fernet
(bibliothèque `cryptography`). La clé doit être générée une seule fois
par environnement et copiée dans `.env.local`.

**Générer la clé :**

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

La commande affiche une chaîne de 44 caractères. L'ajouter dans `.env.local` :

```bash
PA_EXPLORER_ENCRYPTION_KEY=<chaîne de 44 caractères>
```

**Avertissement** : si cette clé est perdue ou modifiée, toutes les
credentials chiffrées en base deviennent illisibles et la base doit être
réinitialisée (`reset_db.ps1`). Ne jamais la committer dans git.

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `APP_NAME` | Nom de l'application | `pa-explorer` |
| `APP_VERSION` | Version de l'application | `0.1.0` |
| `DEBUG` | Mode debug FastAPI | `true` / `false` |
| `DATABASE_URL` | URL de connexion SQLAlchemy | `sqlite:///./pa_explorer.db` |
| `IBM_PA_BASE_URL` | URL de base IBM PA SaaS | `https://eu-central-1.planninganalytics.saas.ibm.com` |
| `IBM_PA_TENANT_ID` | Identifiant du tenant IBM PA | `your-tenant-id` |
| `IBM_PA_API_KEY` | Clé API IBM PA | `your-api-key` |
| `IBM_PA_SERVERS_TTL_SECONDS` | DELAY | 300 |
| `IBM_PA_CUBES_TTL_SECONDS` | DELAY | 300 |
| `IBM_PA_DIMENSIONS_TTL_SECONDS` | DELAY | 300 |
| `PA_EXPLORER_ENCRYPTION_KEY` | Clé Fernet 44 chars pour chiffrer les credentials utilisateur | Générer via `Fernet.generate_key()` |
| `PA_EXPLORER_INITIAL_ADMIN_EMAIL` | Email pré-autorisé dans UserAllowlist au démarrage | `admin@example.com` |
| `PA_EXPLORER_INITIAL_ADMIN_EMAIL` | EMAIl | `example@mail.com` |
| `AUTH_SESSION_TTL_HOURS` | DELAY | 24 |
| `AUTH_MAGIC_LINK_TTL_MINUTES` | DELAY | 15 |

## Endpoints

| Méthode | Route | Description |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Statut du service et de la base |
| `GET` | `/api/v1/servers` | Liste des serveurs TM1 |
| `POST` | `/api/v1/servers/refresh` | Force le rafraîchissement |
| `GET` | `/api/v1/servers/{name}/cubes` | Liste des cubes d'un serveur |
| `GET` | `/api/v1/servers/{name}/cubes/{cube}/dimensions` | Liste des dimensions |
| `POST` | `/api/v1/auth/request` | Demander un magic link |
| `GET` | `/api/v1/auth/verify` | Vérifier le magic link |

## Structure du projet

```bash
pa-explorer/
├── app/
│   ├── main.py          # Point d'entrée FastAPI
│   ├── config.py        # Configuration via .env
│   ├── database.py      # SQLAlchemy engine et session
│   ├── models/          # Modèles ORM
│   ├── routers/         # Endpoints par domaine
│   └── schemas/         # Schémas Pydantic (request/response)
├── .env.example         # Template des variables d'env
├── requirements.txt
└── README.md
```
