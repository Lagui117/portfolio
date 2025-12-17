/**
 * Composant Layout avec Navbar.
 * Enveloppe les pages protegees.
 */

import React from 'react';
import Navbar from './Navbar';
import '../styles/layout.css';

function Layout({ children }) {
  return (
    <div className="layout">
      <Navbar />
      <main className="layout-content">
        {children}
      </main>
      <footer className="layout-footer">
        <p>PredictWise - Plateforme educative</p>
        <p className="disclaimer">
          Les predictions sont experimentales et ne constituent pas des conseils 
          financiers ou de pari.
        </p>
      </footer>
    </div>
  );
}

export default Layout;
