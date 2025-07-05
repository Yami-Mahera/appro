import React, { useState, useEffect } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  ShareIcon,
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import apiService from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import DashboardBuilder from '../components/DashboardBuilder';
import DashboardViewer from '../components/DashboardViewer';

interface Dashboard {
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

const DashboardsPersonnalises: React.FC = () => {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(null);
  const [showBuilder, setShowBuilder] = useState(false);
  const [showViewer, setShowViewer] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    fetchDashboards();
  }, []);

  const fetchDashboards = async () => {
    try {
      setLoading(true);
      const data = await apiService.getDashboardsPersonnalises();
      setDashboards(data);
    } catch (error) {
      console.error('Erreur lors du chargement des dashboards:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDashboard = () => {
    setSelectedDashboard(null);
    setEditMode(false);
    setShowBuilder(true);
  };

  const handleEditDashboard = (dashboard: Dashboard) => {
    setSelectedDashboard(dashboard);
    setEditMode(true);
    setShowBuilder(true);
  };

  const handleViewDashboard = (dashboard: Dashboard) => {
    setSelectedDashboard(dashboard);
    setShowViewer(true);
  };

  const handleDeleteDashboard = async (dashboardId: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce tableau de bord ?')) {
      try {
        // API call would be here when delete endpoint is available
        console.log('Suppression du dashboard:', dashboardId);
        await fetchDashboards();
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  const handleSaveDashboard = async (dashboardData: any) => {
    try {
      if (editMode && selectedDashboard) {
        // Update existing dashboard
        console.log('Mise à jour du dashboard:', dashboardData);
      } else {
        // Create new dashboard
        await apiService.createDashboardPersonnalise(dashboardData);
      }
      setShowBuilder(false);
      await fetchDashboards();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
    }
  };

  if (showBuilder) {
    return (
      <DashboardBuilder
        dashboard={selectedDashboard}
        isEdit={editMode}
        onSave={handleSaveDashboard}
        onCancel={() => setShowBuilder(false)}
      />
    );
  }

  if (showViewer && selectedDashboard) {
    return (
      <DashboardViewer
        dashboard={selectedDashboard}
        onClose={() => setShowViewer(false)}
        onEdit={() => {
          setShowViewer(false);
          handleEditDashboard(selectedDashboard);
        }}
      />
    );
  }

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tableaux de Bord Personnalisés</h1>
          <p className="mt-1 text-sm text-gray-500">
            Créez et gérez vos tableaux de bord personnalisés pour suivre vos KPIs
          </p>
        </div>
        <button
          onClick={handleCreateDashboard}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Nouveau Tableau de Bord
        </button>
      </div>

      {/* Dashboards Grid */}
      {dashboards.length === 0 ? (
        <div className="text-center py-12">
          <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun tableau de bord</h3>
          <p className="mt-1 text-sm text-gray-500">
            Commencez par créer votre premier tableau de bord personnalisé.
          </p>
          <div className="mt-6">
            <button
              onClick={handleCreateDashboard}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Créer un tableau de bord
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboards.map((dashboard) => (
            <div
              key={dashboard.id}
              className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200"
            >
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <ChartBarIcon className="h-8 w-8 text-blue-500" />
                    <div className="ml-3">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {dashboard.nom}
                      </h3>
                      {dashboard.description && (
                        <p className="text-sm text-gray-500 truncate">
                          {dashboard.description}
                        </p>
                      )}
                    </div>
                  </div>
                  {dashboard.partage && (
                    <ShareIcon className="h-5 w-5 text-green-500" title="Partagé" />
                  )}
                </div>

                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{dashboard.widgets?.length || 0} widgets</span>
                    <span>
                      Modifié le {new Date(dashboard.updated_at).toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                </div>

                <div className="mt-6 flex space-x-3">
                  <button
                    onClick={() => handleViewDashboard(dashboard)}
                    className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <EyeIcon className="h-4 w-4 mr-1" />
                    Voir
                  </button>
                  <button
                    onClick={() => handleEditDashboard(dashboard)}
                    className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <PencilIcon className="h-4 w-4 mr-1" />
                    Modifier
                  </button>
                  <button
                    onClick={() => handleDeleteDashboard(dashboard.id)}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-red-50 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Stats */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Statistiques</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <DocumentTextIcon className="h-8 w-8 text-blue-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total</p>
                <p className="text-2xl font-bold text-gray-900">{dashboards.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <ShareIcon className="h-8 w-8 text-green-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Partagés</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboards.filter(d => d.partage).length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center">
              <Cog6ToothIcon className="h-8 w-8 text-purple-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Widgets Total</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboards.reduce((total, d) => total + (d.widgets?.length || 0), 0)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardsPersonnalises;