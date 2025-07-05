import React, { useState, useEffect } from 'react';
import { XMarkIcon, CheckIcon } from '@heroicons/react/24/outline';
import apiService from '../../services/api';

interface Widget {
  id: string;
  type: string;
  title: string;
  config: any;
  position: { x: number; y: number; w: number; h: number };
}

interface WidgetConfigModalProps {
  widget: Widget;
  onSave: (widget: Widget) => void;
  onCancel: () => void;
}

const WidgetConfigModal: React.FC<WidgetConfigModalProps> = ({
  widget,
  onSave,
  onCancel
}) => {
  const [config, setConfig] = useState({
    title: widget.title,
    ...widget.config
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setConfig((prev: any) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSave = () => {
    const updatedWidget = {
      ...widget,
      title: config.title,
      config: { ...config, title: undefined } // Remove title from config as it's separate
    };
    onSave(updatedWidget);
  };

  const renderConfigFields = () => {
    switch (widget.type) {
      case 'stats_card':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Source de données</label>
              <select
                name="dataSource"
                value={config.dataSource || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="total_fournisseurs">Total Fournisseurs</option>
                <option value="total_articles">Total Articles</option>
                <option value="total_commandes">Total Commandes</option>
                <option value="alertes_non_lues">Alertes Non Lues</option>
                <option value="articles_stock_bas">Articles Stock Bas</option>
                <option value="commandes_en_cours">Commandes En Cours</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Couleur</label>
              <select
                name="color"
                value={config.color || 'blue'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="blue">Bleu</option>
                <option value="green">Vert</option>
                <option value="purple">Violet</option>
                <option value="red">Rouge</option>
                <option value="orange">Orange</option>
                <option value="indigo">Indigo</option>
              </select>
            </div>
          </div>
        );

      case 'bar_chart':
      case 'line_chart':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Source de données</label>
              <select
                name="dataSource"
                value={config.dataSource || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="commandes_par_mois">Commandes par Mois</option>
                <option value="articles_par_famille">Articles par Famille</option>
                <option value="evolution_stock">Évolution Stock</option>
                <option value="kpi_delais">KPI Délais</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Période</label>
              <select
                name="periode"
                value={config.periode || '6_mois'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="1_mois">1 Mois</option>
                <option value="3_mois">3 Mois</option>
                <option value="6_mois">6 Mois</option>
                <option value="1_an">1 An</option>
              </select>
            </div>
          </div>
        );

      case 'pie_chart':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Répartition</label>
              <select
                name="repartition"
                value={config.repartition || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="articles_par_famille">Articles par Famille</option>
                <option value="commandes_par_statut">Commandes par Statut</option>
                <option value="fournisseurs_par_pays">Fournisseurs par Pays</option>
                <option value="alertes_par_type">Alertes par Type</option>
              </select>
            </div>
          </div>
        );

      case 'data_table':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Table de données</label>
              <select
                name="tableType"
                value={config.tableType || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="fournisseurs">Fournisseurs</option>
                <option value="articles">Articles</option>
                <option value="commandes">Commandes</option>
                <option value="alertes">Alertes</option>
                <option value="articles_stock_bas">Articles Stock Bas</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Nombre de lignes</label>
              <input
                type="number"
                name="rowCount"
                value={config.rowCount || 10}
                onChange={handleInputChange}
                min="5"
                max="100"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>
        );

      case 'kpi_metric':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Métrique KPI</label>
              <select
                name="kpiType"
                value={config.kpiType || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="taux_service_client">Taux Service Client</option>
                <option value="delai_moyen_livraison">Délai Moyen Livraison</option>
                <option value="taux_rupture_stock">Taux Rupture Stock</option>
                <option value="rotation_stock">Rotation Stock</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Format d'affichage</label>
              <select
                name="displayFormat"
                value={config.displayFormat || 'percentage'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="percentage">Pourcentage</option>
                <option value="number">Nombre</option>
                <option value="currency">Monétaire</option>
                <option value="days">Jours</option>
              </select>
            </div>
          </div>
        );

      case 'alert_list':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Type d'alertes</label>
              <select
                name="alertType"
                value={config.alertType || 'all'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="all">Toutes les alertes</option>
                <option value="stock_bas">Stock Bas</option>
                <option value="retard_livraison">Retard Livraison</option>
                <option value="seuil_atteint">Seuil Atteint</option>
                <option value="commande_urgente">Commande Urgente</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Nombre maximum</label>
              <input
                type="number"
                name="maxAlerts"
                value={config.maxAlerts || 5}
                onChange={handleInputChange}
                min="3"
                max="20"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>
        );

      case 'trend_indicator':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Indicateur</label>
              <select
                name="indicator"
                value={config.indicator || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="evolution_commandes">Évolution Commandes</option>
                <option value="evolution_stock">Évolution Stock</option>
                <option value="performance_fournisseurs">Performance Fournisseurs</option>
                <option value="satisfaction_client">Satisfaction Client</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Période de comparaison</label>
              <select
                name="compareWith"
                value={config.compareWith || 'previous_month'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="previous_month">Mois précédent</option>
                <option value="previous_quarter">Trimestre précédent</option>
                <option value="previous_year">Année précédente</option>
              </select>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-8 text-gray-500">
            Configuration non disponible pour ce type de widget
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Configuration du Widget
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Titre du widget */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Titre du widget
            </label>
            <input
              type="text"
              name="title"
              value={config.title}
              onChange={handleInputChange}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Titre du widget"
            />
          </div>

          {/* Taille du widget */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Largeur</label>
              <select
                name="width"
                value={widget.position.w}
                onChange={(e) => {
                  const newWidget = {
                    ...widget,
                    position: { ...widget.position, w: parseInt(e.target.value) }
                  };
                  // Update the widget position
                }}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="3">Petite (3)</option>
                <option value="4">Moyenne (4)</option>
                <option value="6">Grande (6)</option>
                <option value="8">Très Grande (8)</option>
                <option value="12">Pleine largeur (12)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Hauteur</label>
              <select
                name="height"
                value={widget.position.h}
                onChange={(e) => {
                  const newWidget = {
                    ...widget,
                    position: { ...widget.position, h: parseInt(e.target.value) }
                  };
                  // Update the widget position
                }}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="2">Petite (2)</option>
                <option value="3">Moyenne (3)</option>
                <option value="4">Grande (4)</option>
                <option value="6">Très Grande (6)</option>
              </select>
            </div>
          </div>

          {/* Configuration spécifique au type de widget */}
          {renderConfigFields()}
        </div>

        <div className="mt-6 flex justify-end space-x-3">
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
            Sauvegarder
          </button>
        </div>
      </div>
    </div>
  );
};

export default WidgetConfigModal;