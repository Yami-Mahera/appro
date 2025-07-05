import React, { useState, useEffect } from 'react';
import { 
  XMarkIcon, 
  PlusIcon, 
  CheckIcon,
  Cog6ToothIcon,
  TrashIcon,
  ArrowsPointingOutIcon
} from '@heroicons/react/24/outline';
import apiService from '../../services/api';
import WidgetConfigModal from './WidgetConfigModal';
import WidgetPreview from './WidgetPreview';

interface Widget {
  id: string;
  type: string;
  title: string;
  config: any;
  position: { x: number; y: number; w: number; h: number };
}

interface Dashboard {
  id?: string;
  nom: string;
  description?: string;
  widgets: Widget[];
  layout: any;
  partage: boolean;
}

interface DashboardBuilderProps {
  dashboard?: Dashboard | null;
  isEdit: boolean;
  onSave: (dashboard: Dashboard) => void;
  onCancel: () => void;
}

const DashboardBuilder: React.FC<DashboardBuilderProps> = ({
  dashboard,
  isEdit,
  onSave,
  onCancel
}) => {
  const [formData, setFormData] = useState<Dashboard>({
    nom: '',
    description: '',
    widgets: [],
    layout: { cols: 12, rows: 10 },
    partage: false
  });
  const [availableWidgets, setAvailableWidgets] = useState<any[]>([]);
  const [showWidgetModal, setShowWidgetModal] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<Widget | null>(null);
  const [draggedWidget, setDraggedWidget] = useState<any>(null);

  useEffect(() => {
    if (dashboard && isEdit) {
      setFormData({
        nom: dashboard.nom,
        description: dashboard.description || '',
        widgets: dashboard.widgets || [],
        layout: dashboard.layout || { cols: 12, rows: 10 },
        partage: dashboard.partage || false
      });
    }
    fetchAvailableWidgets();
  }, [dashboard, isEdit]);

  const fetchAvailableWidgets = async () => {
    try {
      const data = await apiService.getWidgetsDisponibles();
      // S'assurer que data est un tableau
      if (Array.isArray(data)) {
        setAvailableWidgets(data);
      } else {
        console.error('Les données des widgets ne sont pas un tableau:', data);
        setAvailableWidgets([]);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des widgets:', error);
      // Fallback avec des widgets par défaut
      setAvailableWidgets([
        { type: 'kpi_card', name: 'Carte KPI', category: 'Métriques' },
        { type: 'chart_line', name: 'Graphique Courbes', category: 'Graphiques' },
        { type: 'chart_bar', name: 'Graphique Barres', category: 'Graphiques' },
        { type: 'chart_pie', name: 'Graphique Camembert', category: 'Graphiques' },
        { type: 'table', name: 'Tableau de Données', category: 'Données' },
        { type: 'gauge', name: 'Jauge', category: 'KPIs' }
      ]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleAddWidget = (widgetType: any) => {
    const newWidget: Widget = {
      id: `widget_${Date.now()}`,
      type: widgetType.type,
      title: `Nouveau ${widgetType.name}`,
      config: {},
      position: { x: 0, y: 0, w: 4, h: 3 }
    };
    setSelectedWidget(newWidget);
    setShowWidgetModal(true);
  };

  const handleConfigureWidget = (widget: Widget) => {
    setSelectedWidget(widget);
    setShowWidgetModal(true);
  };

  const handleSaveWidget = (widgetConfig: Widget) => {
    setFormData(prev => {
      const existingIndex = prev.widgets.findIndex(w => w.id === widgetConfig.id);
      if (existingIndex >= 0) {
        // Update existing widget
        const updatedWidgets = [...prev.widgets];
        updatedWidgets[existingIndex] = widgetConfig;
        return { ...prev, widgets: updatedWidgets };
      } else {
        // Add new widget
        return { ...prev, widgets: [...prev.widgets, widgetConfig] };
      }
    });
    setShowWidgetModal(false);
    setSelectedWidget(null);
  };

  const handleDeleteWidget = (widgetId: string) => {
    setFormData(prev => ({
      ...prev,
      widgets: prev.widgets.filter(w => w.id !== widgetId)
    }));
  };

  const handleSave = () => {
    if (!formData.nom.trim()) {
      alert('Veuillez saisir un nom pour le tableau de bord');
      return;
    }
    onSave(formData);
  };

  const widgetCategories = availableWidgets.reduce((acc: any, widget) => {
    const category = widget.category || 'Autres';
    if (!acc[category]) acc[category] = [];
    acc[category].push(widget);
    return acc;
  }, {});

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              {isEdit ? 'Modifier' : 'Créer'} un Tableau de Bord
            </h1>
            <p className="text-sm text-gray-500">
              Configurez votre tableau de bord personnalisé
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <CheckIcon className="h-4 w-4 mr-1 inline" />
              Enregistrer
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Widget Library */}
        <div className="w-80 bg-white shadow-sm border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Configuration</h3>
            
            {/* Dashboard Info */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Nom du tableau de bord *
                </label>
                <input
                  type="text"
                  name="nom"
                  value={formData.nom}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Ex: Dashboard Ventes"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Description optionnelle..."
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="partage"
                  checked={formData.partage}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Partager avec d'autres utilisateurs
                </label>
              </div>
            </div>

            <hr className="my-6" />

            {/* Available Widgets */}
            <h4 className="text-md font-medium text-gray-900 mb-3">Widgets Disponibles</h4>
            <div className="space-y-3">
              {Object.entries(widgetCategories).map(([category, widgets]: [string, any]) => (
                <div key={category}>
                  <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    {category}
                  </h5>
                  <div className="space-y-1">
                    {widgets.map((widget: any) => (
                      <button
                        key={widget.type}
                        onClick={() => handleAddWidget(widget)}
                        className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 rounded-md transition-colors duration-150"
                      >
                        <PlusIcon className="h-4 w-4 mr-2 inline" />
                        {widget.name}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Canvas */}
        <div className="flex-1 p-6 overflow-auto">
          <div className="bg-white rounded-lg shadow-sm min-h-full p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Aperçu du Tableau de Bord
              </h3>
              <span className="text-sm text-gray-500">
                {formData.widgets.length} widget(s)
              </span>
            </div>

            {formData.widgets.length === 0 ? (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <ArrowsPointingOutIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  Aucun widget ajouté
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Commencez par ajouter des widgets depuis la bibliothèque.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-12 gap-4 min-h-96">
                {formData.widgets.map((widget) => (
                  <div
                    key={widget.id}
                    className={`col-span-${widget.position.w} relative bg-gray-50 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow`}
                    style={{ 
                      gridColumn: `span ${widget.position.w}`,
                      minHeight: `${widget.position.h * 60}px`
                    }}
                  >
                    <div className="absolute top-2 right-2 flex space-x-1">
                      <button
                        onClick={() => handleConfigureWidget(widget)}
                        className="p-1 text-gray-400 hover:text-blue-600 rounded"
                        title="Configurer"
                      >
                        <Cog6ToothIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteWidget(widget.id)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                        title="Supprimer"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <WidgetPreview widget={widget} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Widget Configuration Modal */}
      {showWidgetModal && selectedWidget && (
        <WidgetConfigModal
          widget={selectedWidget}
          onSave={handleSaveWidget}
          onCancel={() => {
            setShowWidgetModal(false);
            setSelectedWidget(null);
          }}
        />
      )}
    </div>
  );
};

export default DashboardBuilder;