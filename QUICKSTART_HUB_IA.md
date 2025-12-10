# 🚀 Quick Start - Hub IA

## En 3 étapes

### 1️⃣ Démarrer le backend
```bash
cd backend
source venv/bin/activate
python -m app.main
```

✅ Backend disponible sur http://localhost:8000

### 2️⃣ Démarrer le frontend
```bash
cd frontend
npm run dev
```

✅ Frontend disponible sur http://localhost:5173

### 3️⃣ Tester le Hub IA
1. Ouvrir http://localhost:5173
2. Cliquer sur "Inscription" ou "Connexion"
3. **Vous êtes automatiquement redirigé vers `/hub`** 🎉
4. Cliquer sur les cartes pour naviguer

---

## 🎯 Ce que vous verrez

### Page d'accueil Hub (/hub)

```
┌─────────────────────────────────────┐
│        🎯 PREDICTWISE               │
│    Plateforme éducative d'analyse   │
│                                     │
│  Bienvenue, [votre username] !      │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────┐  ┌─────────────┐  │
│  │⚽  Analyse   │  │📈  Analyse   │  │
│  │   Sportive  │  │  Financière  │  │
│  │             │  │             │  │
│  │ [Accéder]   │  │ [Accéder]   │  │
│  └─────────────┘  └─────────────┘  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🤖 Suggestion IA du jour     │   │
│  │ Sur les derniers matchs...   │   │
│  │ [Propulsé par GPT-4]         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📊 Vos statistiques          │   │
│  │ [42] [25] [17] [68]          │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 🧪 Tests rapides

### Test 1 : Suggestion IA
```bash
curl http://localhost:8000/api/v1/ai/daily-suggestion
```

**Résultat attendu :**
```json
{
  "title": "Suggestion IA du jour",
  "text": "Sur les derniers matchs..."
}
```

### Test 2 : Statistiques (avec token)
```bash
# 1. Se connecter et récupérer le token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# 2. Utiliser le token pour les stats
curl http://localhost:8000/api/v1/users/stats \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

**Résultat attendu :**
```json
{
  "total_predictions": 0,
  "sports_predictions": 0,
  "finance_predictions": 0,
  "total_consultations": 0,
  "member_since": "2024-12-10T10:30:00"
}
```

---

## 📋 Checklist de vérification

Après démarrage, vérifiez :

- [ ] Page `/hub` accessible après login
- [ ] Logo "PredictWise" redirige vers `/hub`
- [ ] Navbar affiche "Hub IA" en premier
- [ ] Message "Bienvenue, [username]" visible
- [ ] Deux cartes (Sports/Finance) cliquables
- [ ] Suggestion IA affichée (texte chargé)
- [ ] Statistiques utilisateur affichées (si données)
- [ ] Animations hover fonctionnent
- [ ] Design responsive sur mobile

---

## 🎨 Personnalisation rapide

### Changer les couleurs
```css
/* frontend/src/pages/HomeHub.css */

/* Background principal */
.hub-layout {
  background: #020617; /* Modifier ici */
}

/* Couleur accent Sports */
.hub-card-sports {
  border-top: 3px solid #22c55e; /* Modifier ici */
}

/* Couleur accent Finance */
.hub-card-finance {
  border-top: 3px solid #38bdf8; /* Modifier ici */
}
```

### Ajouter une suggestion IA
```python
# backend/app/api/v1/ai.py

suggestions = [
    # ... suggestions existantes
    {
        'title': 'Votre nouveau titre',
        'text': 'Votre nouveau texte de suggestion...'
    }
]
```

### Modifier les icônes
```jsx
// frontend/src/pages/HomeHub.jsx

<div className="hub-card-icon">🏆</div>  {/* Changer l'emoji */}
```

---

## 🔧 Dépannage

### Problème : Page blanche après login
**Solution :** Vérifier que la route `/hub` est dans App.jsx
```jsx
<Route path="/hub" element={
  <PrivateRoute><HomeHub /></PrivateRoute>
} />
```

### Problème : Suggestion IA ne charge pas
**Solution :** Vérifier que le backend est démarré
```bash
curl http://localhost:8000/api/v1/ai/daily-suggestion
```

### Problème : Stats à 0 même après utilisation
**Solution :** Les modèles Prediction/Consultation doivent exister en DB
- Créer des prédictions via `/sports/predict/1`
- Les stats se mettent à jour automatiquement

### Problème : CSS ne s'applique pas
**Solution :** Vérifier que HomeHub.css est importé
```jsx
import './HomeHub.css'  // Dans HomeHub.jsx
```

---

## 📚 Documentation complète

Pour plus de détails :

- **Documentation technique :** `docs/HUB_IA_DOCUMENTATION.md`
- **Guide implémentation :** `docs/HUB_IA_IMPLEMENTATION.md`
- **Résumé exécutif :** `docs/HUB_IA_SUMMARY.md`
- **Visuel ASCII :** `docs/HUB_IA_VISUAL.txt`

---

## 🎉 C'est tout !

Votre Hub IA est maintenant **opérationnel** et **prêt à l'emploi** ! 🚀

**Temps total de setup : ~2 minutes**

---

## 🔮 Prochaines étapes suggérées

1. **Tester sur mobile** (ouvrir depuis votre téléphone)
2. **Créer quelques prédictions** pour voir les stats monter
3. **Personnaliser les couleurs** selon vos préférences
4. **Ajouter vos propres suggestions IA**
5. **Connecter GPT** pour suggestions dynamiques (voir `docs/INSTALLATION_OPENAI.md`)

**Amusez-vous bien avec PredictWise !** 🎯
