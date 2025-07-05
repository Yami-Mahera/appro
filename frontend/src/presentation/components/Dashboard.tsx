import React, { useState, useEffect } from 'react';
import { 
  BuildingOfficeIcon,
  CubeIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ShareIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { DashboardStats } from '../../data/types';
import apiService from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { formatNumber } from '../../common/utils';
import StockEvolutionChart from './StockEvolutionChart';
import DashboardBuilder from './DashboardBuilder';
import DashboardViewer from './DashboardViewer';

interface CustomDashboard {
  id: string;
  nom: string;
  description?: string;
  user_id: string;
  widgets: any[];
  layout: any;
  partage: boolean;
  created_at: string;
  updated_at: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiService.getDashboardStats();
        setStats(data);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      name: 'Fournisseurs',
      stat: stats?.total_fournisseurs || 0,
      icon: BuildingOfficeIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Articles',
      stat: stats?.total_articles || 0,
      icon: CubeIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Commandes',
      stat: stats?.total_commandes || 0,
      icon: DocumentTextIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Alertes non lues',
      stat: stats?.alertes_non_lues || 0,
      icon: ExclamationTriangleIcon,
      color: 'bg-red-500',
    },
  ];

  const alertCards = [
    {
      name: 'Articles en stock bas',
      stat: stats?.articles_stock_bas || 0,
      icon: ArrowTrendingDownIcon,
      color: 'bg-orange-500',
    },
    {
      name: 'Commandes en cours',
      stat: stats?.commandes_en_cours || 0,
      icon: ClockIcon,
      color: 'bg-indigo-500',
    },
  ];

  // Mock data for charts
  const monthlyData = [
    { name: 'Jan', commandes: 65, articles: 28 },
    { name: 'Fév', commandes: 59, articles: 48 },
    { name: 'Mar', commandes: 80, articles: 40 },
    { name: 'Avr', commandes: 81, articles: 19 },
    { name: 'Mai', commandes: 56, articles: 86 },
    { name: 'Jun', commandes: 55, articles: 27 },
  ];

  const categoryData = [
    { name: 'Électronique', value: 35, color: '#3B82F6' },
    { name: 'Fournitures', value: 25, color: '#10B981' },
    { name: 'Outils', value: 20, color: '#8B5CF6' },
    { name: 'Consommables', value: 20, color: '#F59E0B' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Vue d'ensemble de votre système d'approvisionnement
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div key={card.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`${card.color} rounded-md p-3`}>
                    <card.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {card.name}
                    </dt>
                    <dd className="text-2xl font-bold text-gray-900">
                      {formatNumber(card.stat)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Alert Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        {alertCards.map((card) => (
          <div key={card.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`${card.color} rounded-md p-3`}>
                    <card.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {card.name}
                    </dt>
                    <dd className="text-2xl font-bold text-gray-900">
                      {formatNumber(card.stat)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Évolution mensuelle
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="commandes" fill="#3B82F6" name="Commandes" />
              <Bar dataKey="articles" fill="#10B981" name="Articles" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Répartition par catégorie
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Graphique d'évolution du stock avancé */}
      <StockEvolutionChart className="mt-6" />

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Activité récente
          </h3>
          <div className="flow-root">
            <ul className="-mb-8">
              <li className="relative pb-8">
                <div className="relative flex space-x-3">
                  <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                    <DocumentTextIcon className="h-5 w-5 text-white" />
                  </div>
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p className="text-sm text-gray-500">
                        Nouvelle commande créée <span className="font-medium text-gray-900">CMD-20250101-001</span>
                      </p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      Il y a 2h
                    </div>
                  </div>
                </div>
              </li>
              <li className="relative pb-8">
                <div className="relative flex space-x-3">
                  <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                    <CubeIcon className="h-5 w-5 text-white" />
                  </div>
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p className="text-sm text-gray-500">
                        Stock mis à jour pour <span className="font-medium text-gray-900">Article A123</span>
                      </p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      Il y a 4h
                    </div>
                  </div>
                </div>
              </li>
              <li className="relative">
                <div className="relative flex space-x-3">
                  <div className="h-8 w-8 rounded-full bg-orange-500 flex items-center justify-center ring-8 ring-white">
                    <ExclamationTriangleIcon className="h-5 w-5 text-white" />
                  </div>
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p className="text-sm text-gray-500">
                        Alerte stock bas pour <span className="font-medium text-gray-900">Vis M6</span>
                      </p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      Il y a 6h
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;