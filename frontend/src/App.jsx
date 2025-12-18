import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Routes/Pages
import LandingPage from './routes/LandingPage';
import SignupPage from './routes/SignupPage';
import LoginPage from './routes/LoginPage';
import AppHubPage from './routes/AppHubPage';
import SportsDashboardPage from './routes/SportsDashboardPage';
import FinanceDashboardPage from './routes/FinanceDashboardPage';
import DashboardPremium from './routes/DashboardPremium';
import ProfilePage from './routes/ProfilePage';

// Admin Pages
import AdminDashboard from './pages/AdminDashboard';
import AdminUsers from './pages/AdminUsers';
import AdminActivity from './pages/AdminActivity';

// New Dashboard Pages
import DashboardAdvanced from './pages/DashboardAdvanced';
import PredictionHistory from './pages/PredictionHistory';
import UserDashboard from './pages/UserDashboard';
import History from './pages/History';
import Watchlist from './pages/Watchlist';

// Components
import Layout from './components/Layout';
import AdminRoute from './components/AdminRoute';

// Styles
import './styles/global.css';
import './styles/variables.premium.css';

/**
 * Composant de route protegee.
 * Redirige vers /login si pas de token JWT.
 */
function PrivateRoute({ children }) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

/**
 * Application principale PredictWise.
 */
function App() {
  return (
    <Routes>
      {/* Routes publiques */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/login" element={<LoginPage />} />
      
      {/* Dashboard Premium (nouvelle route) */}
      <Route
        path="/app/premium"
        element={
          <PrivateRoute>
            <DashboardPremium />
          </PrivateRoute>
        }
      />
      
      {/* Routes protegees */}
      <Route
        path="/app"
        element={
          <PrivateRoute>
            <Layout>
              <AppHubPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/app/sports"
        element={
          <PrivateRoute>
            <Layout>
              <SportsDashboardPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/app/finance"
        element={
          <PrivateRoute>
            <Layout>
              <FinanceDashboardPage />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/app/profile"
        element={
          <PrivateRoute>
            <Layout>
              <ProfilePage />
            </Layout>
          </PrivateRoute>
        }
      />
      
      {/* Routes Admin */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <Layout>
              <AdminDashboard />
            </Layout>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <AdminRoute>
            <Layout>
              <AdminUsers />
            </Layout>
          </AdminRoute>
        }
      />
      <Route
        path="/admin/activity"
        element={
          <AdminRoute>
            <Layout>
              <AdminActivity />
            </Layout>
          </AdminRoute>
        }
      />
      
      {/* Redirections de compatibilite */}
      <Route path="/dashboard" element={<Navigate to="/app" replace />} />
      <Route path="/app/admin" element={<Navigate to="/admin" replace />} />
      
      {/* Dashboard Avancé et Historique */}
      <Route
        path="/app/dashboard"
        element={
          <PrivateRoute>
            <Layout>
              <DashboardAdvanced />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/app/history"
        element={
          <PrivateRoute>
            <Layout>
              <PredictionHistory />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route path="/history" element={<Navigate to="/app/history" replace />} />
      
      {/* Watchlist / Favoris */}
      <Route
        path="/app/watchlist"
        element={
          <PrivateRoute>
            <Layout>
              <Watchlist />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route path="/watchlist" element={<Navigate to="/app/watchlist" replace />} />
      
      {/* Route par defaut */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
