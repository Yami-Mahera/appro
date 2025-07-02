import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from './hooks/useAuth';
import ProtectedRoute from './presentation/components/ProtectedRoute';
import Layout from './presentation/components/Layout';
import Dashboard from './presentation/components/Dashboard';
import Login from './presentation/screens/Login';
import "./App.css";

// Placeholder components for other routes
const Fournisseurs = () => (
  <div>
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Fournisseurs</h1>
    <p className="text-gray-600">Interface de gestion des fournisseurs (en développement)</p>
  </div>
);

const Articles = () => (
  <div>
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Articles</h1>
    <p className="text-gray-600">Interface de gestion des articles (en développement)</p>
  </div>
);

const Commandes = () => (
  <div>
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Commandes</h1>
    <p className="text-gray-600">Interface de gestion des commandes (en développement)</p>
  </div>
);

const Alertes = () => (
  <div>
    <h1 className="text-2xl font-bold text-gray-900 mb-4">Alertes</h1>
    <p className="text-gray-600">Interface de gestion des alertes (en développement)</p>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/">
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/fournisseurs"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/fournisseurs">
                    <Fournisseurs />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/articles"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/articles">
                    <Articles />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/commandes"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/commandes">
                    <Commandes />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/alertes"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/alertes">
                    <Alertes />
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

export default App;
