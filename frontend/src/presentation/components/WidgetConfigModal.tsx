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
  
  const [position, setPosition] = useState(widget.position);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setConfig((prev: any) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handlePositionChange = (dimension: 'w' | 'h', value: number) => {
    setPosition(prev => ({
      ...prev,
      [dimension]: value
    }));
  };

  const handleSave = () => {
    const updatedWidget = {
      ...widget,
      title: config.title,
      config: { ...config, title: undefined }, // Remove title from config as it's separate
      position: position
    };
    onSave(updatedWidget);
  };

  const renderConfigFields = () => {
    switch (widget.type) {
      case 'kpi_card':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Métrique KPI</label>
              <select
                name="kpiType"
                value={config.kpiType || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="total_fournisseurs">Total Fournisseurs</option>
                <option value="total_articles">Total Articles</option>
                <option value="total_commandes">Total Commandes</option>
                <option value="alertes_non_lues">Alertes Non Lues</option>
                <option value="articles_stock_bas">Articles Stock Bas</option>
                <option value="commandes_en_cours">Commandes En Cours</option>
                <option value="taux_service_client">Taux Service Client</option>
                <option value="delai_livraison">Délai Moyen Livraison</option>
                <option value="commandes_traitees">Commandes Traitées</option>
                <option value="rupture_stock">Taux Rupture Stock</option>
                <option value="rotation_stock">Rotation Stock</option>
                <option value="performance_fournisseur">Performance Fournisseur</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Couleur</label>
              <select
                name="color"
                value={config.color || 'blue'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="blue">Bleu</option>
                <option value="green">Vert</option>
                <option value="purple">Violet</option>
                <option value="red">Rouge</option>
                <option value="orange">Orange</option>
                <option value="indigo">Indigo</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Format d'affichage</label>
              <select
                name="displayFormat"
                value={config.displayFormat || 'percentage'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="percentage">Pourcentage (%)</option>
                <option value="number">Nombre</option>
                <option value="currency">Monétaire (€)</option>
                <option value="days">Jours</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Objectif/Seuil</label>
              <input
                type="number"
                name="target"
                value={config.target || ''}
                onChange={handleInputChange}
                placeholder="Ex: 95 pour 95%"
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>
        );

      case 'chart_line':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Source de données</label>
              <select
                name="dataSource"
                value={config.dataSource || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="commandes_par_mois">Commandes par Mois</option>
                <option value="evolution_stock">Évolution du Stock</option>
                <option value="evolution_commandes">Évolution des Commandes</option>
                <option value="evolution_kpis">Évolution des KPIs</option>
                <option value="tendance_ventes">Tendance des Ventes</option>
                <option value="performance_fournisseurs">Performance Fournisseurs</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Période d'affichage</label>
              <select
                name="periode"
                value={config.periode || '3_mois'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="7_jours">7 Jours</option>
                <option value="1_mois">1 Mois</option>
                <option value="3_mois">3 Mois</option>
                <option value="6_mois">6 Mois</option>
                <option value="1_an">1 An</option>
                <option value="2_ans">2 Ans</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Style de ligne</label>
              <select
                name="lineStyle"
                value={config.lineStyle || 'solid'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="solid">Ligne continue</option>
                <option value="dashed">Ligne pointillée</option>
                <option value="dotted">Points</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Couleur du graphique</label>
              <select
                name="chartColor"
                value={config.chartColor || 'blue'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="blue">Bleu</option>
                <option value="green">Vert</option>
                <option value="purple">Violet</option>
                <option value="red">Rouge</option>
                <option value="orange">Orange</option>
                <option value="gradient">Dégradé</option>
              </select>
            </div>
          </div>
        );

      case 'chart_bar':
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
                <option value="commandes_par_fournisseur">Commandes par Fournisseur</option>
                <option value="articles_par_famille">Articles par Famille</option>
                <option value="alertes_par_type">Alertes par Type</option>
                <option value="performance_mensuelle">Performance Mensuelle</option>
                <option value="volume_ventes">Volume des Ventes</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Orientation</label>
              <select
                name="orientation"
                value={config.orientation || 'vertical'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="vertical">Barres verticales</option>
                <option value="horizontal">Barres horizontales</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Nombre maximum d'éléments</label>
              <input
                type="number"
                name="maxItems"
                value={config.maxItems || 10}
                onChange={handleInputChange}
                min="5"
                max="50"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Schéma de couleurs</label>
              <select
                name="colorScheme"
                value={config.colorScheme || 'blue'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="blue">Tons de bleu</option>
                <option value="green">Tons de vert</option>
                <option value="multicolor">Multicolore</option>
                <option value="gradient">Dégradé</option>
              </select>
            </div>
          </div>
        );

      case 'chart_pie':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Répartition des données</label>
              <select
                name="dataSource"
                value={config.dataSource || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="repartition_commandes">Répartition des Commandes</option>
                <option value="repartition_stock">Répartition du Stock</option>
                <option value="repartition_alertes">Répartition des Alertes</option>
                <option value="repartition_fournisseurs">Répartition par Fournisseur</option>
                <option value="repartition_familles">Répartition par Famille</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Type d'affichage</label>
              <select
                name="displayType"
                value={config.displayType || 'pie'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="pie">Camembert classique</option>
                <option value="doughnut">Anneau (Donut)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Afficher les pourcentages</label>
              <select
                name="showPercentage"
                value={config.showPercentage || 'true'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="true">Oui</option>
                <option value="false">Non</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Position de la légende</label>
              <select
                name="legendPosition"
                value={config.legendPosition || 'right'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="top">En haut</option>
                <option value="bottom">En bas</option>
                <option value="left">À gauche</option>
                <option value="right">À droite</option>
                <option value="none">Masquer</option>
              </select>
            </div>
          </div>
        );

      case 'table':
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
                <option value="alertes_recentes">Alertes Récentes</option>
                <option value="commandes_urgentes">Commandes Urgentes</option>
                <option value="stock_bas">Articles en Stock Bas</option>
                <option value="fournisseurs_actifs">Fournisseurs Actifs</option>
                <option value="derniers_mouvements">Derniers Mouvements</option>
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
            <div>
              <label className="block text-sm font-medium text-gray-700">Colonnes à afficher</label>
              <select
                name="columns"
                value={config.columns || 'default'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="default">Colonnes par défaut</option>
                <option value="minimal">Vue minimale</option>
                <option value="detailed">Vue détaillée</option>
                <option value="custom">Personnalisé</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Tri par défaut</label>
              <select
                name="defaultSort"
                value={config.defaultSort || 'date_desc'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="date_desc">Date (plus récent)</option>
                <option value="date_asc">Date (plus ancien)</option>
                <option value="name_asc">Nom (A-Z)</option>
                <option value="priority_desc">Priorité (haute)</option>
              </select>
            </div>
          </div>
        );

      case 'gauge':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Métrique à mesurer</label>
              <select
                name="metric"
                value={config.metric || ''}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">Sélectionner...</option>
                <option value="performance_fournisseur">Performance Fournisseur</option>
                <option value="taux_service">Taux de Service</option>
                <option value="niveau_stock">Niveau de Stock</option>
                <option value="qualite_livraison">Qualité des Livraisons</option>
                <option value="satisfaction_client">Satisfaction Client</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Valeur minimale</label>
              <input
                type="number"
                name="minValue"
                value={config.minValue || 0}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Valeur maximale</label>
              <input
                type="number"
                name="maxValue"
                value={config.maxValue || 100}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Seuils d'alerte</label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  name="warningThreshold"
                  value={config.warningThreshold || 70}
                  onChange={handleInputChange}
                  placeholder="Seuil Warning"
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                <input
                  type="number"
                  name="criticalThreshold"
                  value={config.criticalThreshold || 90}
                  onChange={handleInputChange}
                  placeholder="Seuil Critique"
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Couleurs des zones</label>
              <select
                name="colorZones"
                value={config.colorZones || 'traffic_light'}
                onChange={handleInputChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="traffic_light">Feu tricolore (Vert/Orange/Rouge)</option>
                <option value="blue_gradient">Dégradé de bleu</option>
                <option value="performance">Performance (Rouge/Jaune/Vert)</option>
              </select>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-8 text-gray-500">
            <div className="mb-4">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p className="text-lg font-medium">Configuration avancée en cours de développement</p>
            <p className="text-sm mt-2">Ce type de widget sera bientôt personnalisable avec de nombreuses options.</p>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 dark:bg-gray-900 dark:bg-opacity-75 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border border-gray-200 dark:border-gray-600 w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Configuration du Widget
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Titre du widget */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Titre du widget
            </label>
            <input
              type="text"
              name="title"
              value={config.title}
              onChange={handleInputChange}
              className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Titre du widget"
            />
          </div>

          {/* Taille du widget */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Largeur</label>
              <select
                name="width"
                value={position.w}
                onChange={(e) => handlePositionChange('w', parseInt(e.target.value))}
                className="mt-1 block w-full border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
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
                value={position.h}
                onChange={(e) => handlePositionChange('h', parseInt(e.target.value))}
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