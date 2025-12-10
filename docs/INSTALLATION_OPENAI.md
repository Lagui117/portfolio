# Guide d'installation - Intégration OpenAI et APIs

Ce guide vous accompagne dans la configuration complète de PredictWise avec les nouvelles fonctionnalités de prédiction par IA.

## Prérequis

- Python 3.9+
- Node.js 18+
- Compte OpenAI (pour l'analyse GPT)
- (Optionnel) Comptes API pour données sports/finance

---

## Installation Backend

### 1. Installer les dépendances Python

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Installer les dépendances (y compris openai)
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer le fichier .env
nano .env  # ou vim, code, etc.
```

**Configuration minimale** (avec données mock) :

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=votre-cle-secrete-unique
JWT_SECRET_KEY=votre-jwt-secret-unique

# Database
DATABASE_URL=sqlite:///predictwise.db

# CORS
CORS_ORIGINS=http://localhost:5173

# OpenAI (OBLIGATOIRE pour GPT)
OPENAI_API_KEY=sk-proj-...  # Votre clé OpenAI

# Mode mock (pour développement sans APIs payantes)
USE_MOCK_SPORTS_API=true
USE_MOCK_FINANCE_API=false  # yfinance est gratuit
```

### 3. Obtenir une clé API OpenAI

1. Créer un compte sur [OpenAI Platform](https://platform.openai.com/)
2. Aller dans [API Keys](https://platform.openai.com/api-keys)
3. Cliquer "Create new secret key"
4. Copier la clé (commence par `sk-`)
5. L'ajouter dans `.env` : `OPENAI_API_KEY=sk-...`

**Coûts estimés** :
- GPT-4o-mini : ~$0.001-0.003 par prédiction
- Crédit gratuit de $5 pour nouveaux comptes
- Budget recommandé : $10-20/mois pour développement

### 4. (Optionnel) Configurer l'API Sports

**Option 1 : API-FOOTBALL (RapidAPI)**

1. Créer un compte sur [RapidAPI](https://rapidapi.com/)
2. S'abonner à [API-FOOTBALL](https://rapidapi.com/api-sports/api/api-football)
3. Plan gratuit : 100 requêtes/jour
4. Copier votre clé API RapidAPI
5. Ajouter dans `.env` :

```bash
SPORTS_API_KEY=votre-rapidapi-key
SPORTS_API_HOST=api-football-v1.p.rapidapi.com
USE_MOCK_SPORTS_API=false
```

**Option 2 : The Odds API**

1. S'inscrire sur [The Odds API](https://the-odds-api.com/)
2. Plan gratuit : 500 requêtes/mois
3. Ajouter dans `.env` :

```bash
SPORTS_API_KEY=votre-odds-api-key
SPORTS_API_PROVIDER=odds-api
USE_MOCK_SPORTS_API=false
```

**Option 3 : Mode Mock (recommandé pour débuter)**

```bash
USE_MOCK_SPORTS_API=true
# Génère des données réalistes mais simulées
```

### 5. Initialiser la base de données

```bash
# Toujours dans l'environnement virtuel activé
python -c "from app.core.database import db; from app.main import create_app; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"
```

### 6. Lancer le backend

```bash
# Option 1 : Avec Flask directement
python app/main.py

# Option 2 : Avec le script de démarrage
chmod +x ../run_backend.sh
../run_backend.sh
```

Le backend devrait être accessible sur `http://localhost:5000`

---

## Installation Frontend

### 1. Installer les dépendances Node.js

```bash
cd frontend

# Installer les packages
npm install
```

### 2. Configurer les variables d'environnement

```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer le fichier .env
nano .env
```

**Configuration** :

```bash
VITE_API_BASE_URL=http://localhost:5000/api/v1
VITE_APP_NAME=PredictWise
VITE_ENABLE_SPORTS=true
VITE_ENABLE_FINANCE=true
```

### 3. Lancer le frontend

```bash
# Mode développement
npm run dev

# Le frontend sera accessible sur http://localhost:5173
```

---

## Tester l'intégration

### Test 1 : Backend seul

```bash
# Vérifier que le backend répond
curl http://localhost:5000/health

# Devrait retourner:
# {"status":"healthy","version":"1.0.0","environment":"development"}
```

### Test 2 : Créer un compte

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123"
  }'

# Sauvegarder le token retourné
```

### Test 3 : Prédiction sports

```bash
# Remplacer YOUR_TOKEN par le token obtenu ci-dessus
curl -X GET "http://localhost:5000/api/v1/sports/predict/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Devrait retourner une prédiction complète avec analyse GPT
```

### Test 4 : Prédiction finance

```bash
curl -X GET "http://localhost:5000/api/v1/finance/predict/AAPL" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Devrait retourner une analyse financière avec GPT
```

### Test 5 : Interface web

1. Ouvrir `http://localhost:5173` dans le navigateur
2. S'inscrire avec un compte
3. Aller sur la page Sports
4. Essayer une prédiction (entrer un match ID comme "1" ou "2")
5. Vérifier que les sections apparaissent :
   - Données du match
   - Prédiction ML
   - Analyse GPT

---

## Vérification de la configuration

### Script de diagnostic

Créer un fichier `backend/check_config.py` :

```python
import os
from dotenv import load_load_dotenv()

print("=== Configuration PredictWise ===\n")

# Variables essentielles
essential = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
}

print("Variables essentielles:")
for key, value in essential.items():
    status = "✓ OK" if value else "✗ MANQUANT"
    masked = value[:10] + "..." if value else "Non défini"
    print(f"  {status} {key}: {masked}")

# Variables optionnelles
optional = {
    'SPORTS_API_KEY': os.getenv('SPORTS_API_KEY'),
    'FINANCE_API_KEY': os.getenv('FINANCE_API_KEY'),
    'USE_MOCK_SPORTS_API': os.getenv('USE_MOCK_SPORTS_API', 'true'),
    'USE_MOCK_FINANCE_API': os.getenv('USE_MOCK_FINANCE_API', 'false'),
}

print("\nVariables optionnelles:")
for key, value in optional.items():
    status = "✓" if value else "○"
    print(f"  {status} {key}: {value or 'Non défini'}")

# Test OpenAI
print("\n=== Test OpenAI ===")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print("✓ Client OpenAI initialisé avec succès")
except Exception as e:
    print(f"✗ Erreur OpenAI: {e}")

# Test des services
print("\n=== Test Services ===")
try:
    from app.services.gpt_service import gpt_service
    print(f"✓ GPT Service: {'Activé' if gpt_service.client else 'Mode dégradé'}")
except Exception as e:
    print(f"✗ Erreur GPT Service: {e}")

try:
    from app.services.sports_api_service import sports_api_service
    print(f"✓ Sports API: {'Mock' if sports_api_service.use_mock else 'Réel'}")
except Exception as e:
    print(f"✗ Erreur Sports API: {e}")

try:
    from app.services.finance_api_service import finance_api_service
    print(f"✓ Finance API: {'Mock' if finance_api_service.use_mock else 'Réel (yfinance)'}")
except Exception as e:
    print(f"✗ Erreur Finance API: {e}")

print("\n=== Fin du diagnostic ===")
```

Exécuter :

```bash
cd backend
source venv/bin/activate
python check_config.py
```

---

## Problèmes courants

### Erreur : "ModuleNotFoundError: No module named 'openai'"

**Solution** :
```bash
pip install openai==1.6.1
```

### Erreur : "OpenAI API key not found"

**Solution** :
1. Vérifier que `.env` existe : `ls -la backend/.env`
2. Vérifier le contenu : `cat backend/.env | grep OPENAI`
3. Relancer le serveur après modification du `.env`

### Erreur : "GPT analysis unavailable"

**Causes possibles** :
1. Clé API invalide
2. Quota OpenAI dépassé
3. Problème de connexion internet

**Vérification** :
```bash
# Tester la clé API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Les prédictions sont lentes (>10 secondes)

**Causes** :
- Appel GPT prend 2-4 secondes
- Multiples appels API externes

**Solutions** :
- Utiliser le mode mock en développement
- Implémenter un système de cache (Redis)
- Passer à GPT-3.5-turbo (plus rapide)

### Frontend ne peut pas contacter le backend

**Vérifications** :
1. Backend lancé : `curl http://localhost:5000/health`
2. CORS configuré : vérifier `CORS_ORIGINS` dans `.env`
3. URL correcte dans frontend : vérifier `VITE_API_BASE_URL`

---

## Déploiement en production

### Checklist de sécurité

- [ ] Changer `SECRET_KEY` et `JWT_SECRET_KEY`
- [ ] Utiliser PostgreSQL au lieu de SQLite
- [ ] Activer HTTPS
- [ ] Configurer les variables d'environnement sur le serveur
- [ ] Ne JAMAIS committer `.env`
- [ ] Restreindre CORS aux domaines autorisés
- [ ] Configurer des limites de taux (rate limiting)
- [ ] Monitorer l'utilisation de l'API OpenAI

### Variables d'environnement production

```bash
FLASK_ENV=production
DEBUG=False
SECRET_KEY=une-tres-longue-cle-aleatoire-securisee
JWT_SECRET_KEY=une-autre-cle-aleatoire-securisee
DATABASE_URL=postgresql://user:password@host:5432/dbname
CORS_ORIGINS=https://votre-domaine.com
OPENAI_API_KEY=sk-...
```

### Déploiement recommandé

- **Backend** : Heroku, Railway, Render, AWS EC2
- **Frontend** : Vercel, Netlify, AWS S3 + CloudFront
- **Base de données** : PostgreSQL (Heroku Postgres, AWS RDS)

---

## Support et ressources

- **Documentation OpenAI** : https://platform.openai.com/docs
- **Documentation Flask** : https://flask.palletsprojects.com/
- **Documentation React** : https://react.dev/

Pour toute question, consulter la documentation complète dans `/docs/`.
