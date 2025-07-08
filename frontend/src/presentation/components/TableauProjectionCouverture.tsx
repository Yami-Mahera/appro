import React, { useState, useEffect } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import apiService from '../../services/api';
import Pagination from './Pagination';

interface ProjectionData {
  semaine: number;
  dateDebut: string;
  dateFin: string;
  stockDebut: number;
  stockFin: number;
  qmPrevisionnelle: number;
  consommationPrevue: number;
  consommationReelle?: number;
  status: 'normal' | 'attention' | 'critique';
  cms: number;
  cmc: number;
  couvertureActuelle: number;
}

interface TableauProjectionCouvertureProps {
  articleId?: string;
  className?: string;
}

const TableauProjectionCouverture: React.FC<TableauProjectionCouvertureProps> = ({ 
  articleId,
  className = '' 
}) => {
  const [projections, setProjections] = useState<ProjectionData[]>([]);
  const [articles, setArticles] = useState<any[]>([]);
  const [selectedArticleId, setSelectedArticleId] = useState<string>(articleId || '');
  const [loading, setLoading] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [timeRange, setTimeRange] = useState<number>(26); // 26 semaines par défaut

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [totalItems, setTotalItems] = useState(0);

  useEffect(() => {
    loadArticles();
  }, []);

  useEffect(() => {
    if (selectedArticleId) {
      loadProjectionData();
    }
  }, [selectedArticleId, timeRange, currentPage, itemsPerPage]);

  const loadArticles = async () => {
    try {
      const response = await apiService.getArticles({ limit: 100 });
      const data = response.articles || response;
      setArticles(data);
      if (!selectedArticleId && data.length > 0) {
        setSelectedArticleId(data[0].id);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des articles:', error);
    }
  };

  const loadProjectionData = async () => {
    if (!selectedArticleId) return;

    try {
      setLoading(true);
      const [evolution, couverture] = await Promise.all([
        apiService.getEvolutionStock(selectedArticleId, timeRange),
        apiService.getCalculCouverture(selectedArticleId)
      ]);

      // Transformer les données d'évolution en format de projection
      const projectionsData: ProjectionData[] = evolution.evolution.map((item: any, index: number) => {
        const stockDebut = item.stock_debut || 0;
        const stockFin = item.stock_fin || 0;
        const consommationPrevue = item.prevision_consommation || 0;
        
        // Calculer la QM prévisionnelle basée sur les calculs de couverture
        const qmPrevisionnelle = Math.max(0, couverture.quantite_maximale_commande - stockFin);
        
        // Déterminer le statut basé sur la couverture et les seuils
        let status: 'normal' | 'attention' | 'critique' = 'normal';
        const couvertureActuelle = stockFin / (consommationPrevue || 1);
        
        if (couvertureActuelle < couverture.couverture_minimale_securite / 2) {
          status = 'critique';
        } else if (couvertureActuelle < couverture.couverture_minimale_securite) {
          status = 'attention';
        }

        return {
          semaine: index + 1,
          dateDebut: new Date(item.date_debut).toLocaleDateString('fr-FR'),
          dateFin: new Date(item.date_fin).toLocaleDateString('fr-FR'),
          stockDebut,
          stockFin,
          qmPrevisionnelle,
          consommationPrevue,
          consommationReelle: item.consommation_reelle,
          status,
          cms: couverture.couverture_minimale_securite,
          cmc: couverture.couverture_maximale_commande,
          couvertureActuelle
        };
      });

      setTotalItems(projectionsData.length);
      setProjections(projectionsData);
    } catch (error) {
      console.error('Erreur lors du chargement des projections:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRowExpansion = (semaine: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(semaine)) {
      newExpanded.delete(semaine);
    } else {
      newExpanded.add(semaine);
    }
    setExpandedRows(newExpanded);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critique':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'attention':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const selectedArticle = articles.find(a => a.id === selectedArticleId);

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm ${className}`}>
      {/* En-tête */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Tableau de projection de la couverture de stock
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Prévisions et calculs sophistiqués selon les modalités CMS/CMC/QM
            </p>
          </div>
          
          {/* Contrôles */}
          <div className="flex space-x-4">
            <div className="flex flex-col">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Article</label>
              <select
                value={selectedArticleId}
                onChange={(e) => setSelectedArticleId(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Sélectionner un article</option>
                {articles.map((article) => (
                  <option key={article.id} value={article.id}>
                    {article.reference} - {article.nom}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex flex-col">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Période</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value={13}>13 semaines</option>
                <option value={26}>26 semaines</option>
                <option value={52}>52 semaines</option>
              </select>
            </div>
          </div>
        </div>

        {/* Informations article sélectionné */}
        {selectedArticle && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Référence:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedArticle.reference}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Stock actuel:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedArticle.stock_actuel}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Seuil minimum:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedArticle.seuil_min}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Prix unitaire:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedArticle.prix_unitaire}€</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tableau de projection */}
      <div className="overflow-x-auto">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Semaine
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Période
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Stock Début
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Stock Fin
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  QM Prévisionnelle
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Consommation Prévue
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Couverture
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {projections.map((projection) => (
                <React.Fragment key={projection.semaine}>
                  <tr className={`hover:bg-gray-50 dark:hover:bg-gray-700 ${projection.status === 'critique' ? 'bg-red-50 dark:bg-red-900/20' : projection.status === 'attention' ? 'bg-yellow-50 dark:bg-yellow-900/20' : ''}`}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {projection.semaine}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      <div className="flex flex-col">
                        <span>Du {projection.dateDebut}</span>
                        <span>Au {projection.dateFin}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {projection.stockDebut}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      <span className={`font-medium ${projection.stockFin < projection.cms ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'}`}>
                        {projection.stockFin}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      <span className={`px-2 py-1 rounded ${projection.qmPrevisionnelle > 0 ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'}`}>
                        {projection.qmPrevisionnelle}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      <div className="flex flex-col">
                        <span>Prévue: {projection.consommationPrevue}</span>
                        {projection.consommationReelle !== undefined && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            Réelle: {projection.consommationReelle}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      <div className="flex flex-col text-xs">
                        <span>Actuelle: {projection.couvertureActuelle.toFixed(1)}</span>
                        <span className="text-gray-500 dark:text-gray-400">CMS: {projection.cms.toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusColor(projection.status)}`}>
                        {projection.status === 'critique' ? 'Critique' : 
                         projection.status === 'attention' ? 'Attention' : 'Normal'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      <button
                        onClick={() => toggleRowExpansion(projection.semaine)}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                      >
                        {expandedRows.has(projection.semaine) ? (
                          <ChevronUpIcon className="h-4 w-4" />
                        ) : (
                          <ChevronDownIcon className="h-4 w-4" />
                        )}
                      </button>
                    </td>
                  </tr>
                  
                  {/* Ligne détaillée */}
                  {expandedRows.has(projection.semaine) && (
                    <tr className="bg-gray-50 dark:bg-gray-700">
                      <td colSpan={9} className="px-6 py-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div className="space-y-2">
                            <h4 className="font-medium text-gray-900 dark:text-white">Calculs de Couverture</h4>
                            <div className="space-y-1 text-gray-600 dark:text-gray-400">
                              <div>CMS (Couverture Minimale Sécurité): <span className="font-medium">{projection.cms.toFixed(2)}</span></div>
                              <div>CMC (Couverture Maximale Commande): <span className="font-medium">{projection.cmc.toFixed(2)}</span></div>
                              <div>Couverture Actuelle: <span className="font-medium">{projection.couvertureActuelle.toFixed(2)}</span></div>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <h4 className="font-medium text-gray-900 dark:text-white">Détails Stock</h4>
                            <div className="space-y-1 text-gray-600 dark:text-gray-400">
                              <div>Variation: <span className="font-medium">{(projection.stockFin - projection.stockDebut).toFixed(0)}</span></div>
                              <div>Rotation: <span className="font-medium">{projection.consommationPrevue > 0 ? (projection.stockFin / projection.consommationPrevue).toFixed(1) : 'N/A'} semaines</span></div>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <h4 className="font-medium text-gray-900 dark:text-white">Recommandations</h4>
                            <div className="space-y-1 text-gray-600 dark:text-gray-400">
                              {projection.status === 'critique' && (
                                <div className="text-red-600 dark:text-red-400 font-medium">⚠️ Commande urgente recommandée</div>
                              )}
                              {projection.status === 'attention' && (
                                <div className="text-yellow-600 dark:text-yellow-400 font-medium">⚡ Surveiller de près</div>
                              )}
                              {projection.qmPrevisionnelle > 0 && (
                                <div className="text-blue-600 dark:text-blue-400">📦 QM optimale: {projection.qmPrevisionnelle}</div>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Légende */}
      <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Légende</h4>
        <div className="flex flex-wrap gap-4 text-xs text-gray-600 dark:text-gray-400">
          <div className="flex items-center">
            <span className="w-3 h-3 bg-green-100 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded mr-2"></span>
            Normal: Stock suffisant
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-yellow-100 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded mr-2"></span>
            Attention: Proche du seuil minimum
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-red-100 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded mr-2"></span>
            Critique: En dessous du seuil de sécurité
          </div>
          <div className="ml-8">
            <strong>CMS:</strong> Couverture Minimale Sécurité | <strong>CMC:</strong> Couverture Maximale Commande | <strong>QM:</strong> Quantité Maximale commande
          </div>
        </div>
      </div>
    </div>
  );
};

export default TableauProjectionCouverture;