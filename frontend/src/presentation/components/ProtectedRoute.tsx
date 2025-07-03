import React, { ReactNode } from 'react';
import { useAuth } from '../../hooks/useAuth';
import Login from '../screens/Login';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRoles?: string[];
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRoles = [],
  requiredRole
}) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  // Check role requirements
  const roles = requiredRole ? [requiredRole] : requiredRoles;
  if (roles.length > 0 && user && !roles.includes(user.role)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Accès refusé</h2>
          <p className="text-gray-600">
            Vous n'avez pas les permissions nécessaires pour accéder à cette page.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Rôle requis: {roles.join(' ou ')}
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;