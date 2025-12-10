# 🚀 QuickStart - PredictWise

**Temps estimé:** 5 minutes

---

## 1️⃣ Installation (2 min)

```bash
./install.sh
```

Ou manuellement :
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

---

## 2️⃣ Entraîner les modèles ML (2 min)

```bash
cd ml/scripts
python train_sports_model.py
python train_finance_model.py
cd ../..
```

**Sortie attendue:**
- `ml/models/sports_model.pkl` (13 MB)
- `ml/models/finance_model.pkl` (1.2 KB)
- `ml/models/finance_scaler.pkl` (1.4 KB)

---

## 3️⃣ Lancer l'application (1 min)

### Terminal 1 - Backend
```bash
./run_backend.sh
```
✅ Backend ready: http://localhost:5000

### Terminal 2 - Frontend
```bash
./run_frontend.sh
```
✅ Frontend ready: http://localhost:5173

---

## 4️⃣ Tester (30 sec)

### Ouvrir dans le navigateur
http://localhost:5173

### Créer un compte
- Cliquer sur "Sign up"
- Email: `test@example.com`
- Username: `testuser`
- Password: `Test1234!`

### Tester les prédictions

**Sports:**
1. Aller dans "Sports"
2. Cliquer sur "Predict Match"
3. Sélectionner deux équipes
4. Voir la prédiction (HOME_WIN/DRAW/AWAY_WIN)

**Finance:**
1. Aller dans "Finance"
2. Entrer un symbole: `AAPL`
3. Cliquer sur "Analyze"
4. Voir les indicateurs techniques
5. Cliquer sur "Predict Trend"
6. Voir la prédiction (UP/DOWN)

---

## 🔗 URLs Importantes

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Application React |
| **API** | http://localhost:5000/api/v1 | API REST |
| **Swagger** | http://localhost:5000/api/docs | Documentation interactive |
| **Health** | http://localhost:5000/health | Status du backend |

---

## 🧪 Vérifications Rapides

### Backend fonctionne ?
```bash
curl http://localhost:5000/health
# Doit retourner: {"status":"healthy","version":"1.0.0"}
```

### Modèles chargés ?
```bash
cd backend
source venv/bin/activate
python -c "from app.services.prediction_service import get_prediction_service; print(get_prediction_service().get_models_info())"
```

### Frontend build OK ?
```bash
cd frontend
npm run build
# Doit créer frontend/dist/
```

---

## 🐛 Dépannage Express

### Backend ne démarre pas
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend ne démarre pas
```bash
cd frontend
npm install
```

### Modèles non trouvés
```bash
cd ml/scripts
python train_sports_model.py
python train_finance_model.py
```

### Port déjà utilisé
```bash
# Tuer le processus sur le port 5000
lsof -ti:5000 | xargs kill -9

# Tuer le processus sur le port 5173
lsof -ti:5173 | xargs kill -9
```

---

## 📚 Documentation Complète

- **README principal:** [README.md](README.md)
- **Documentation ML:** [docs/ML_OVERVIEW.md](docs/ML_OVERVIEW.md)
- **API Spec:** [docs/API_SPEC.md](docs/API_SPEC.md)
- **Santé du projet:** [HEALTH_CHECK.md](HEALTH_CHECK.md)

---

## 🎯 Prochaines Étapes

Après avoir testé l'application :

1. **Explorer l'API avec Swagger** - http://localhost:5000/api/docs
2. **Évaluer les modèles ML** - `cd ml/scripts && python evaluate_models.py`
3. **Lire la documentation technique** - [docs/TECHNICAL.md](docs/TECHNICAL.md)
4. **Personnaliser le projet** - Modifier les modèles, ajouter des features

---

**Bon développement ! 🚀**
