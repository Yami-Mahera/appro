import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../../services/api';
import type { DashboardStats } from '../../common/types';
import {
  BuildingOfficeIcon,
  CubeIcon,
  ShoppingCartIcon,
  BellIcon,
  ExclamationTriangleIcon,
  TruckIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getStats();
      setStats(data);
    } catch (err) {
      setError('Erreur lors du chargement des statistiques');
      console.error('Dashboard stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">{error}</div>
        <button
          onClick={loadStats}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Réessayer
        </button>
      </div>
    );
  }

  const dashboardCards = [
    {
      title: 'Fournisseurs',
      value: stats?.total_fournisseurs || 0,
      icon: BuildingOfficeIcon,
      color: 'blue',
      link: '/fournisseurs',
    },
    {
      title: 'Articles',
      value: stats?.total_articles || 0,
      icon: CubeIcon,
      color: 'green',
      link: '/articles',
    },
    {
      title: 'Commandes',
      value: stats?.total_commandes || 0,
      icon: ShoppingCartIcon,
      color: 'purple',
      link: '/commandes',
    },
    {
      title: 'Alertes',
      value: stats?.alertes_non_lues || 0,
      icon: BellIcon,
      color: 'red',
      link: '/alertes',
    },
  ];

  const alerts = [
    {
      title: 'Articles en stock bas',
      value: stats?.articles_stock_bas || 0,
      icon: ExclamationTriangleIcon,
      color: 'orange',
      description: 'Articles nécessitant un réapprovisionnement',
    },
    {
      title: 'Commandes en cours',
      value: stats?.commandes_en_cours || 0,
      icon: TruckIcon,
      color: 'blue',
      description: 'Commandes en attente de livraison',
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Vue d'ensemble de votre système d'approvisionnement
        </p>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {dashboardCards.map((card) => (
          <Link
            key={card.title}
            to={card.link}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <card.icon
                    className={`h-6 w-6 text-${card.color}-500`}
                    aria-hidden="true"
                  />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {card.title}
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {card.value}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Alerts Section */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 mb-8">
        {alerts.map((alert) => (
          <div
            key={alert.title}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <alert.icon
                    className={`h-6 w-6 text-${alert.color}-500`}
                    aria-hidden="true"
                  />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {alert.title}
                    </dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">
                        {alert.value}
                      </div>
                      <div className="text-sm text-gray-500">
                        {alert.description}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Actions rapides
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Link
              to="/fournisseurs"
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <div className="flex-shrink-0">
                <BuildingOfficeIcon className="h-8 w-8 text-blue-500" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="absolute inset-0" aria-hidden="true" />
                <p className="text-sm font-medium text-gray-900">
                  Gérer les fournisseurs
                </p>
                <p className="text-sm text-gray-500 truncate">
                  Ajouter, modifier, consulter
                </p>
              </div>
            </Link>

            <Link
              to="/articles"
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <div className="flex-shrink-0">
                <CubeIcon className="h-8 w-8 text-green-500" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="absolute inset-0" aria-hidden="true" />
                <p className="text-sm font-medium text-gray-900">
                  Gérer les articles
                </p>
                <p className="text-sm text-gray-500 truncate">
                  Stock, prix, seuils
                </p>
              </div>
            </Link>

            <Link
              to="/commandes"
              className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <div className="flex-shrink-0">
                <ShoppingCartIcon className="h-8 w-8 text-purple-500" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="absolute inset-0" aria-hidden="true" />
                <p className="text-sm font-medium text-gray-900">
                  Créer une commande
                </p>
                <p className="text-sm text-gray-500 truncate">
                  Nouvelle commande d'achat
                </p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;