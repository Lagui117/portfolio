/**
 * Watchlist - Page de gestion des favoris.
 * Équipes, ligues, tickers et cryptos suivis.
 */

import { useState, useEffect } from 'react';
import watchlistService from '../services/watchlistService';
import './Watchlist.css';

const Watchlist = () => {
  const [items, setItems] = useState([]);
  const [grouped, setGrouped] = useState({});
  const [counts, setCounts] = useState({});
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Modal d'ajout
  const [showAddModal, setShowAddModal] = useState(false);
  const [newItem, setNewItem] = useState({
    item_type: 'ticker',
    item_id: '',
    item_name: '',
    notes: ''
  });

  useEffect(() => {
    loadWatchlist();
  }, []);

  const loadWatchlist = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await watchlistService.getWatchlist();
      setItems(data.items || []);
      setGrouped(data.grouped || {});
      setCounts(data.counts_by_type || {});
    } catch (err) {
      console.error('Erreur chargement watchlist:', err);
      setError('Impossible de charger la watchlist');
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async () => {
    if (!newItem.item_id || !newItem.item_name) {
      alert('Veuillez remplir les champs obligatoires');
      return;
    }

    try {
      await watchlistService.addToWatchlist(newItem);
      setShowAddModal(false);
      setNewItem({ item_type: 'ticker', item_id: '', item_name: '', notes: '' });
      loadWatchlist();
    } catch (err) {
      if (err.response?.status === 409) {
        alert('Cet item est déjà dans votre watchlist');
      } else {
        alert('Erreur lors de l\'ajout');
      }
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!confirm('Supprimer cet item de la watchlist ?')) return;

    try {
      await watchlistService.removeFromWatchlist(itemId);
      loadWatchlist();
    } catch (err) {
      alert('Erreur lors de la suppression');
    }
  };

  const handleToggleAlerts = async (item) => {
    try {
      await watchlistService.toggleAlerts(item.id, !item.alerts_enabled);
      loadWatchlist();
    } catch (err) {
      alert('Erreur lors de la mise à jour des alertes');
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'team': return '⚽';
      case 'league': return '🏆';
      case 'ticker': return '📈';
      case 'crypto': return '₿';
      default: return '⭐';
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'team': return 'Équipes';
      case 'league': return 'Ligues';
      case 'ticker': return 'Actions';
      case 'crypto': return 'Crypto';
      default: return 'Autres';
    }
  };

  const filteredItems = activeTab === 'all' 
    ? items 
    : items.filter(i => i.item_type === activeTab);

  return (
    <div className="watchlist-page">
      {/* Header */}
      <header className="watchlist-header">
        <div className="header-content">
          <div>
            <h1>⭐ Ma Watchlist</h1>
            <p>Suivez vos équipes et actifs préférés</p>
          </div>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddModal(true)}
          >
            + Ajouter
          </button>
        </div>
      </header>

      {/* Tabs */}
      <nav className="watchlist-tabs">
        <button 
          className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          Tous ({items.length})
        </button>
        {['team', 'league', 'ticker', 'crypto'].map(type => (
          <button 
            key={type}
            className={`tab-btn ${activeTab === type ? 'active' : ''}`}
            onClick={() => setActiveTab(type)}
          >
            {getTypeIcon(type)} {getTypeLabel(type)} ({counts[type] || 0})
          </button>
        ))}
      </nav>

      {/* Content */}
      {loading ? (
        <div className="watchlist-loading">
          <div className="spinner"></div>
          <p>Chargement...</p>
        </div>
      ) : error ? (
        <div className="watchlist-error">
          <span>⚠️</span>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadWatchlist}>Réessayer</button>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="watchlist-empty">
          <span className="empty-icon">📭</span>
          <h3>Votre watchlist est vide</h3>
          <p>Ajoutez des équipes ou des actifs pour les suivre</p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddModal(true)}
          >
            Ajouter un favori
          </button>
        </div>
      ) : (
        <section className="watchlist-grid">
          {filteredItems.map(item => (
            <div key={item.id} className="watchlist-card">
              <div className="card-header">
                <span className="item-type-icon">{getTypeIcon(item.item_type)}</span>
                <span className="item-type-label">{getTypeLabel(item.item_type)}</span>
                <button 
                  className={`alert-toggle ${item.alerts_enabled ? 'active' : ''}`}
                  onClick={() => handleToggleAlerts(item)}
                  title={item.alerts_enabled ? 'Désactiver les alertes' : 'Activer les alertes'}
                >
                  🔔
                </button>
              </div>
              
              <div className="card-body">
                <h3 className="item-name">{item.item_name}</h3>
                <p className="item-id">{item.item_id}</p>
                {item.notes && (
                  <p className="item-notes">{item.notes}</p>
                )}
              </div>
              
              <div className="card-footer">
                <span className="item-date">
                  Ajouté le {new Date(item.created_at).toLocaleDateString('fr-FR')}
                </span>
                <button 
                  className="btn-remove"
                  onClick={() => handleRemoveItem(item.id)}
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Ajouter à la Watchlist</h2>
              <button className="modal-close" onClick={() => setShowAddModal(false)}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Type</label>
                <select 
                  value={newItem.item_type}
                  onChange={e => setNewItem(prev => ({ ...prev, item_type: e.target.value }))}
                >
                  <option value="team">⚽ Équipe</option>
                  <option value="league">🏆 Ligue</option>
                  <option value="ticker">📈 Action</option>
                  <option value="crypto">₿ Crypto</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Identifiant / Symbole *</label>
                <input 
                  type="text"
                  placeholder="Ex: AAPL, PSG, BTC..."
                  value={newItem.item_id}
                  onChange={e => setNewItem(prev => ({ ...prev, item_id: e.target.value }))}
                />
              </div>
              
              <div className="form-group">
                <label>Nom *</label>
                <input 
                  type="text"
                  placeholder="Ex: Apple Inc., Paris Saint-Germain..."
                  value={newItem.item_name}
                  onChange={e => setNewItem(prev => ({ ...prev, item_name: e.target.value }))}
                />
              </div>
              
              <div className="form-group">
                <label>Notes (optionnel)</label>
                <textarea 
                  placeholder="Vos notes personnelles..."
                  value={newItem.notes}
                  onChange={e => setNewItem(prev => ({ ...prev, notes: e.target.value }))}
                />
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowAddModal(false)}
              >
                Annuler
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleAddItem}
              >
                Ajouter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Watchlist;
