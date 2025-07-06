import React, { useState, useEffect } from 'react';
import { 
  XMarkIcon, 
  ExclamationTriangleIcon, 
  ClockIcon, 
  EyeIcon, 
  CheckCircleIcon,
  UserIcon,
  BuildingOfficeIcon,
  CubeIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
  ArrowTopRightOnSquareIcon,
  CheckIcon,
  XCircleIcon
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

interface AlerteDetailModalProps {
  alerte: AlerteAvancee;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (alerteId: string, updates: Partial<AlerteAvancee>) => void;
  onNavigate?: (type: 'article' | 'commande' | 'fournisseur', id: string) => void;
}

const AlerteDetailModal: React.FC<AlerteDetailModalProps> = ({ 
  alerte, 
  isOpen, 
  onClose, 
  onUpdate, 
  onNavigate 
}) => {
  const [loading, setLoading] = useState(false);
  const [articleInfo, setArticleInfo] = useState<any>(null);
  const [commandeInfo, setCommandeInfo] = useState<any>(null);
  const [fournisseurInfo, setFournisseurInfo] = useState<any>(null);

  useEffect(() => {
    if (isOpen && alerte) {
      fetchRelatedData();
    }
  }, [isOpen, alerte]);

  const fetchRelatedData = async () => {
    setLoading(true);
    try {
      // Fetch article info
      if (alerte.article_id) {
        try {
          const articles = await apiService.getArticles();
          const article = articles.find((a: any) => a.id === alerte.article_id);
          setArticleInfo(article || null);
        } catch (error) {
          console.error('Error fetching article:', error);
        }
      }

      // Fetch commande info
      if (alerte.commande_id) {
        try {
          const commandes = await apiService.getCommandes();
          const commande = commandes.find((c: any) => c.id === alerte.commande_id);
          setCommandeInfo(commande || null);
        } catch (error) {
          console.error('Error fetching commande:', error);
        }
      }

      // Fetch fournisseur info
      if (alerte.fournisseur_id) {
        try {
          const fournisseurs = await apiService.getFournisseurs();
          const fournisseur = fournisseurs.find((f: any) => f.id === alerte.fournisseur_id);
          setFournisseurInfo(fournisseur || null);
        } catch (error) {
          console.error('Error fetching fournisseur:', error);
        }
      }
    } catch (error) {
      console.error('Error fetching related data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarquerLue = async () => {
    setLoading(true);
    try {
      await apiService.marquerAlerteLue(alerte.id);
      onUpdate(alerte.id, { lue: true });
    } catch (error) {
      console.error('Error marking alert as read:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleIgnorer = async () => {
    // Pour l'instant, on marque juste comme lue
    await handleMarquerLue();
    onClose();
  };

  const getAlertIcon = (niveau: string) => {
    switch (niveau) {
      case 'critique':
        return <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />;
      case 'urgent':
        return <ClockIcon className="h-6 w-6 text-orange-500" />;
      case 'a_suivre':
        return <EyeIcon className="h-6 w-6 text-yellow-500" />;
      default:
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />
        
        <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full sm:p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              {getAlertIcon(alerte.niveau_alerte)}
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Détails de l'alerte
                </h3>
                <div className="flex items-center space-x-2 mt-1">
                  <span className={classNames(
                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
                    getBadgeColor(alerte.niveau_alerte)
                  )}>
                    {alerte.niveau_alerte.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {alerte.type_alerte === 'nouvelle_commande' ? 'Nouvelle commande' : 'Commande en cours'}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="rounded-md p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="space-y-6">
            {/* Message et recommandation */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Message d'alerte
              </h4>
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                {alerte.message}
              </p>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Recommandation
              </h4>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {alerte.recommandation}
              </p>
            </div>

            {/* Calcul détaillé */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
                Calcul détaillé
              </h4>
              <div className="text-sm text-blue-800 dark:text-blue-200">
                <div className="font-mono bg-blue-100 dark:bg-blue-800 p-2 rounded">
                  {getFormuleExplication(alerte.formule_utilisee, alerte)}
                </div>
                <div className="mt-2">
                  <strong>Formule utilisée :</strong> {alerte.formule_utilisee}
                </div>
                {alerte.urgence_jours !== undefined && (
                  <div className="mt-1">
                    <strong>Urgence :</strong> {alerte.urgence_jours > 0 ? 
                      `${alerte.urgence_jours} jours avant échéance` : 
                      `${Math.abs(alerte.urgence_jours)} jours de retard`
                    }
                  </div>
                )}
              </div>
            </div>

            {/* Informations temporelles */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <CalendarDaysIcon className="h-4 w-4 text-gray-400 mr-2" />
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Dates importantes
                  </h4>
                </div>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-300">
                  <div>
                    <strong>Date d'observation :</strong> {formatDate(alerte.date_observation)}
                  </div>
                  {alerte.date_besoin && (
                    <div>
                      <strong>Date de besoin :</strong> {formatDate(alerte.date_besoin)}
                    </div>
                  )}
                  <div>
                    <strong>Créée le :</strong> {formatDate(alerte.created_at)}
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Délais et couverture
                  </h4>
                </div>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-300">
                  <div>
                    <strong>Délai passation :</strong> {alerte.delai_passation} jours
                  </div>
                  {alerte.delai_acheminement && (
                    <div>
                      <strong>Délai acheminement :</strong> {alerte.delai_acheminement} jours
                    </div>
                  )}
                  {alerte.couverture_prevue && (
                    <div>
                      <strong>Couverture prévue :</strong> {alerte.couverture_prevue.toFixed(1)} jours
                    </div>
                  )}
                  {alerte.couverture_minimale_securite && (
                    <div>
                      <strong>CMS :</strong> {alerte.couverture_minimale_securite.toFixed(1)} jours
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Entités liées */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                Entités liées
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Article */}
                {alerte.article_id && (
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <CubeIcon className="h-4 w-4 text-blue-500 mr-2" />
                        <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                          Article
                        </h5>
                      </div>
                      {onNavigate && (
                        <button
                          onClick={() => onNavigate('article', alerte.article_id!)}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                    {loading ? (
                      <div className="text-xs text-gray-500">Chargement...</div>
                    ) : articleInfo ? (
                      <div className="space-y-1 text-xs text-gray-600 dark:text-gray-300">
                        <div><strong>ID :</strong> {articleInfo.id}</div>
                        <div><strong>Nom :</strong> {articleInfo.nom}</div>
                        <div><strong>Stock :</strong> {articleInfo.stock_actuel}</div>
                      </div>
                    ) : (
                      <div className="text-xs text-gray-500">ID: {alerte.article_id}</div>
                    )}
                  </div>
                )}

                {/* Commande */}
                {alerte.commande_id && (
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-4 w-4 text-green-500 mr-2" />
                        <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                          Commande
                        </h5>
                      </div>
                      {onNavigate && (
                        <button
                          onClick={() => onNavigate('commande', alerte.commande_id!)}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                    {loading ? (
                      <div className="text-xs text-gray-500">Chargement...</div>
                    ) : commandeInfo ? (
                      <div className="space-y-1 text-xs text-gray-600 dark:text-gray-300">
                        <div><strong>ID :</strong> {commandeInfo.id}</div>
                        <div><strong>Statut :</strong> {commandeInfo.statut}</div>
                        <div><strong>Total :</strong> {commandeInfo.total_ht}€</div>
                      </div>
                    ) : (
                      <div className="text-xs text-gray-500">ID: {alerte.commande_id}</div>
                    )}
                  </div>
                )}

                {/* Fournisseur */}
                {alerte.fournisseur_id && (
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <BuildingOfficeIcon className="h-4 w-4 text-purple-500 mr-2" />
                        <h5 className="text-sm font-medium text-gray-900 dark:text-white">
                          Fournisseur
                        </h5>
                      </div>
                      {onNavigate && (
                        <button
                          onClick={() => onNavigate('fournisseur', alerte.fournisseur_id!)}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                    {loading ? (
                      <div className="text-xs text-gray-500">Chargement...</div>
                    ) : fournisseurInfo ? (
                      <div className="space-y-1 text-xs text-gray-600 dark:text-gray-300">
                        <div><strong>ID :</strong> {fournisseurInfo.id}</div>
                        <div><strong>Nom :</strong> {fournisseurInfo.nom}</div>
                        <div><strong>Ville :</strong> {fournisseurInfo.ville}</div>
                      </div>
                    ) : (
                      <div className="text-xs text-gray-500">ID: {alerte.fournisseur_id}</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex justify-end space-x-3">
            {!alerte.lue && (
              <button
                onClick={handleMarquerLue}
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                <CheckIcon className="h-4 w-4 mr-2" />
                Marquer comme lue
              </button>
            )}
            <button
              onClick={handleIgnorer}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <XCircleIcon className="h-4 w-4 mr-2" />
              Ignorer
            </button>
            <button
              onClick={onClose}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlerteDetailModal;