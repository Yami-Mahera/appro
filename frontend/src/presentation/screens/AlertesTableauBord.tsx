import React, { useState, useEffect } from 'react';
import { 
  ExclamationTriangleIcon, 
  ClockIcon, 
  TruckIcon,
  BeakerIcon,
  CheckCircleIcon,
  XMarkIcon,
  FunnelIcon,
  ArrowPathIcon,
  EyeIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { classNames } from '../../common/utils';
import apiService from '../../services/api';

interface AlerteAvancee {
  id: string;
  type_alerte: string;
  niveau_alerte: 'normal' | 'urgent' | 'critique' | 'a_suivre';
  article_id?: string;
  commande_id?: string;
  fournisseur_id?: string;
  formule_utilisee: string;
  valeur_calculee: number;
  date_besoin?: string;
  date_observation: string;
  delai_passation: number;
  couverture_prevue?: number;
  couverture_minimale_securite?: number;
  delai_acheminement?: number;
  message: string;
  recommandation: string;
  urgence_jours?: number;
  lue: boolean;
  created_at: string;
}

const AlertesTableauBord: React.FC = () => {
  const [alertes, setAlertes] = useState<AlerteAvancee[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'urgent' | 'critique' | 'a_suivre'>('all');
  const [typeFilter, setTypeFilter] = useState<'all' | 'nouvelle_commande' | 'commande_en_cours'>('all');
  const [showRead, setShowRead] = useState(false);

  useEffect(() => {
    fetchAlertes();
  }, []);

  const fetchAlertes = async () => {
    setLoading(true);
    try {
      const response = await apiService.getAlertesAvancees();
      setAlertes(response || []);
    } catch (error) {
      console.error('Error fetching advanced alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const genererAlertes = async () => {
    setLoading(true);
    try {
      await apiService.genererAlertesAvancees();
      await fetchAlertes(); // Recharger après génération
    } catch (error) {
      console.error('Error generating alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const marquerCommeLue = async (alerteId: string) => {
    try {
      await apiService.marquerAlerteLue(alerteId);
      setAlertes(prev => prev.map(alerte => 
        alerte.id === alerteId ? { ...alerte, lue: true } : alerte
      ));
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const filteredAlertes = alertes.filter(alerte => {
    if (!showRead && alerte.lue) return false;
    if (filter !== 'all' && alerte.niveau_alerte !== filter) return false;
    if (typeFilter !== 'all' && alerte.type_alerte !== typeFilter) return false;
    return true;
  });

  const getAlertIcon = (niveau: string) => {
    switch (niveau) {
      case 'critique':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'urgent':
        return <ClockIcon className="h-5 w-5 text-orange-500" />;
      case 'a_suivre':
        return <EyeIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    }
  };

  const getBadgeColor = (niveau: string) => {
    switch (niveau) {
      case 'critique':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'urgent':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'a_suivre':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFormuleExplication = (formule: string, alerte: AlerteAvancee) => {
    if (formule === 'Db-Do-Dc') {
      const db = alerte.date_besoin ? new Date(alerte.date_besoin).toLocaleDateString('fr-FR') : 'N/A';
      const do_date = new Date(alerte.date_observation).toLocaleDateString('fr-FR');
      const dc = alerte.delai_passation;
      return `Db (${db}) - Do (${do_date}) - Dc (${dc}j) = ${alerte.valeur_calculee.toFixed(1)} jours`;
    } else if (formule === '(Cp-CMS)/(CMS+da)') {
      const cp = alerte.couverture_prevue || 0;
      const cms = alerte.couverture_minimale_securite || 0;
      const da = alerte.delai_acheminement || 0;
      return `(${cp.toFixed(1)} - ${cms.toFixed(1)}) / (${cms.toFixed(1)} + ${da}) = ${(alerte.valeur_calculee * 100).toFixed(1)}%`;
    }
    return `Valeur: ${alerte.valeur_calculee.toFixed(2)}`;
  };

  // Statistiques pour le header
  const stats = {
    total: alertes.length,
    critiques: alertes.filter(a => a.niveau_alerte === 'critique').length,
    urgentes: alertes.filter(a => a.niveau_alerte === 'urgent').length,
    a_suivre: alertes.filter(a => a.niveau_alerte === 'a_suivre').length,
    non_lues: alertes.filter(a => !a.lue).length
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header avec statistiques */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Tableau de Bord des Alertes
        </h1>
        
        {/* Cartes de statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-8 w-8 text-gray-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Critiques</p>
                <p className="text-2xl font-bold text-red-600">{stats.critiques}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <ClockIcon className="h-8 w-8 text-orange-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Urgentes</p>
                <p className="text-2xl font-bold text-orange-600">{stats.urgentes}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <EyeIcon className="h-8 w-8 text-yellow-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">À Suivre</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.a_suivre}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <BeakerIcon className="h-8 w-8 text-blue-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Non lues</p>
                <p className="text-2xl font-bold text-blue-600">{stats.non_lues}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions et filtres */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={genererAlertes}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              <ArrowPathIcon className={classNames("h-4 w-4 mr-2", loading ? "animate-spin" : "")} />
              Générer Alertes
            </button>
          </div>
          
          <div className="flex flex-wrap gap-2 items-center">
            <div className="flex items-center">
              <FunnelIcon className="h-4 w-4 text-gray-500 mr-2" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Tous niveaux</option>
                <option value="critique">Critiques</option>
                <option value="urgent">Urgentes</option>
                <option value="a_suivre">À suivre</option>
              </select>
            </div>
            
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as any)}
              className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Tous types</option>
              <option value="nouvelle_commande">Nouvelles commandes</option>
              <option value="commande_en_cours">Commandes en cours</option>
            </select>
            
            <label className="flex items-center text-sm">
              <input
                type="checkbox"
                checked={showRead}
                onChange={(e) => setShowRead(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2"
              />
              Afficher lues
            </label>
          </div>
        </div>
      </div>

      {/* Légende des formules */}
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6">
        <h3 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
          Formules de calcul des seuils d'alerte
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-blue-800 dark:text-blue-200">
          <div>
            <strong>Nouvelles commandes :</strong> Db - Do - Dc
            <br />
            <span className="text-blue-600 dark:text-blue-300">
              Db=Date de besoin, Do=Date d'observation, Dc=Délai de passation
            </span>
          </div>
          <div>
            <strong>Commandes en cours :</strong> (Cp-CMS) / (CMS+da)
            <br />
            <span className="text-blue-600 dark:text-blue-300">
              Cp=Couverture prévue, CMS=Couverture minimale sécurité, da=Délai acheminement
            </span>
          </div>
        </div>
      </div>

      {/* Liste des alertes */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {loading ? (
          <div className="p-8 text-center">
            <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-500 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">Chargement des alertes...</p>
          </div>
        ) : filteredAlertes.length === 0 ? (
          <div className="p-8 text-center">
            <CheckCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Aucune alerte correspondante
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              {filter === 'all' && !showRead ? 
                "Toutes les alertes ont été traitées." : 
                "Aucune alerte ne correspond aux filtres sélectionnés."
              }
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredAlertes.map((alerte) => (
              <li key={alerte.id} className={classNames(
                "p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors",
                !alerte.lue ? "bg-blue-50 dark:bg-blue-900/10" : ""
              )}>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {getAlertIcon(alerte.niveau_alerte)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className={classNames(
                          "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
                          getBadgeColor(alerte.niveau_alerte)
                        )}>
                          {alerte.niveau_alerte.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {alerte.type_alerte === 'nouvelle_commande' ? 'Nouvelle commande' : 'Commande en cours'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {!alerte.lue && (
                          <button
                            onClick={() => marquerCommeLue(alerte.id)}
                            className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                            title="Marquer comme lue"
                          >
                            Marquer lue
                          </button>
                        )}
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatDate(alerte.created_at)}
                        </span>
                      </div>
                    </div>
                    
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                      {alerte.message}
                    </h4>
                    
                    <div className="text-xs text-gray-600 dark:text-gray-300 mb-2">
                      <strong>Calcul :</strong> {getFormuleExplication(alerte.formule_utilisee, alerte)}
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                      <strong>Recommandation :</strong> {alerte.recommandation}
                    </p>
                    
                    {alerte.urgence_jours !== undefined && alerte.urgence_jours < 7 && (
                      <div className="flex items-center text-xs text-red-600 dark:text-red-400">
                        <ClockIcon className="h-3 w-3 mr-1" />
                        Action requise dans {Math.abs(alerte.urgence_jours)} jour{Math.abs(alerte.urgence_jours) > 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex-shrink-0">
                    <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {filteredAlertes.length > 0 && (
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {filteredAlertes.length} alerte{filteredAlertes.length > 1 ? 's' : ''} affichée{filteredAlertes.length > 1 ? 's' : ''} 
            sur {alertes.length} au total
          </p>
        </div>
      )}
    </div>
  );
};

export default AlertesTableauBord;