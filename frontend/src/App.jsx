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
import AdminPage from './routes/AdminPage';

// Components
import Layout from './components/Layout';

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
      <Route
        path="/app/admin"
        element={
          <PrivateRoute>
            <Layout>
              <AdminPage />
            </Layout>
          </PrivateRoute>
        }
      />
      
      {/* Route par defaut */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
