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
import UsersAdvanced from './presentation/screens/UsersAdvanced';
import AlertesTableauBord from './presentation/screens/AlertesTableauBord';
import "./App.css";

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
                    <AlertesTableauBord />
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
