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
  const [activeTab, setActiveTab] = useState<'overview' | 'kpi'>('overview');
  
  // States pour les tableaux de bord personnalisés
  const [customDashboards, setCustomDashboards] = useState<CustomDashboard[]>([]);
  const [selectedDashboard, setSelectedDashboard] = useState<CustomDashboard | null>(null);
  const [showBuilder, setShowBuilder] = useState(false);
  const [showViewer, setShowViewer] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    fetchStats();
    fetchCustomDashboards();
  }, []);

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

  const fetchCustomDashboards = async () => {
    try {
      const data = await apiService.getDashboardsPersonnalises();
      setCustomDashboards(data);
    } catch (error) {
      console.error('Erreur lors du chargement des dashboards:', error);
    }
  };

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

  const handleCreateDashboard = () => {
    setSelectedDashboard(null);
    setEditMode(false);
    setShowBuilder(true);
  };

  const handleEditDashboard = (dashboard: CustomDashboard) => {
    setSelectedDashboard(dashboard);
    setEditMode(true);
    setShowBuilder(true);
  };

  const handleViewDashboard = (dashboard: CustomDashboard) => {
    setSelectedDashboard(dashboard);
    setShowViewer(true);
  };

  const handleDeleteDashboard = async (dashboardId: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce dashboard ?')) {
      try {
        await apiService.deleteDashboardPersonnalise(dashboardId);
        fetchCustomDashboards();
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  const handleSaveDashboard = async (dashboardData: any) => {
    try {
      if (editMode && selectedDashboard) {
        await apiService.updateDashboardPersonnalise(selectedDashboard.id, dashboardData);
      } else {
        await apiService.createDashboardPersonnalise(dashboardData);
      }
      fetchCustomDashboards();
      setShowBuilder(false);
      setSelectedDashboard(null);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (showBuilder) {
    return (
      <DashboardBuilder
        dashboard={selectedDashboard}
        isEdit={editMode}
        onSave={handleSaveDashboard}
        onCancel={() => {
          setShowBuilder(false);
          setSelectedDashboard(null);
        }}
      />
    );
  }

  if (showViewer && selectedDashboard) {
    return (
      <DashboardViewer
        dashboard={selectedDashboard}
        onEdit={() => {
          setShowViewer(false);
          handleEditDashboard(selectedDashboard);
        }}
        onClose={() => {
          setShowViewer(false);
          setSelectedDashboard(null);
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Vue d'ensemble et tableaux de bord personnalisés
          </p>
        </div>
        
        {/* Tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'overview'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Vue d'ensemble
          </button>
          <button
            onClick={() => setActiveTab('kpi')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'kpi'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Dashboards KPI
          </button>
        </div>
      </div>

      {/* Contenu basé sur l'onglet actif */}
      {activeTab === 'overview' && (
        <>
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
        </>
      )}

      {/* Section Dashboards KPI */}
      {activeTab === 'kpi' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">
              Tableaux de bord personnalisés
            </h2>
            <button
              onClick={handleCreateDashboard}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Créer un dashboard
            </button>
          </div>

          {customDashboards.length === 0 ? (
            <div className="text-center py-12">
              <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                Aucun dashboard personnalisé
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Créez votre premier tableau de bord pour suivre vos KPIs.
              </p>
              <div className="mt-6">
                <button
                  onClick={handleCreateDashboard}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Créer un dashboard
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {customDashboards.map((dashboard) => (
                <div key={dashboard.id} className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {dashboard.nom}
                    </h3>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleViewDashboard(dashboard)}
                        className="p-2 text-gray-400 hover:text-blue-600"
                        title="Voir"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleEditDashboard(dashboard)}
                        className="p-2 text-gray-400 hover:text-blue-600"
                        title="Éditer"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteDashboard(dashboard.id)}
                        className="p-2 text-gray-400 hover:text-red-600"
                        title="Supprimer"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  {dashboard.description && (
                    <p className="text-sm text-gray-600 mb-4">
                      {dashboard.description}
                    </p>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{dashboard.widgets.length} widgets</span>
                    <span>
                      {dashboard.partage && (
                        <span className="inline-flex items-center text-green-600">
                          <ShareIcon className="h-3 w-3 mr-1" />
                          Partagé
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;