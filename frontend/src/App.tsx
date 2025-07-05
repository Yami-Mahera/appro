import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from './hooks/useAuth';
import ProtectedRoute from './presentation/components/ProtectedRoute';
import Layout from './presentation/components/Layout';
import Dashboard from './presentation/components/Dashboard';
import Login from './presentation/screens/Login';
import FournisseursAdvanced from './presentation/screens/FournisseursAdvanced';
import ArticlesAdvanced from './presentation/screens/ArticlesAdvanced';
import CommandesAdvanced from './presentation/screens/CommandesAdvanced';
import Reporting from './presentation/screens/Reporting';
import GestionStocksAvancee from './presentation/screens/GestionStocksAvancee';
import DashboardsPersonnalises from './presentation/screens/DashboardsPersonnalises';
import UsersAdvanced from './presentation/screens/UsersAdvanced';
import "./App.css";

// Placeholder component for alertes (can be enhanced later)
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
                    <FournisseursAdvanced />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/articles"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/articles">
                    <ArticlesAdvanced />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/commandes"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/commandes">
                    <CommandesAdvanced />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/stocks-avances"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/stocks-avances">
                    <GestionStocksAvancee />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboards"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/dashboards">
                    <DashboardsPersonnalises />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/reporting"
              element={
                <ProtectedRoute>
                  <Layout currentPath="/reporting">
                    <Reporting />
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
            <Route
              path="/users"
              element={
                <ProtectedRoute requiredRole="administrateur">
                  <Layout currentPath="/users">
                    <UsersAdvanced />
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
