import React, { useState, useEffect } from 'react';
import { 
  ClockIcon, 
  TruckIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  EyeIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import apiService from '../../services/api';

interface CommandeEnCours {
  id: string;
  numero_commande: string;
  fournisseur: {
    nom: string;
    code_fournisseur: string;
  };
  status: string;
  date_commande: string;
  date_livraison_prevue: string;
  date_livraison_reelle?: string;
  total_ttc: number;
  nb_articles: number;
  priorite: 'normale' | 'urgent' | 'critique';
  retard_jours: number;
  progression: number;
  alertes: string[];
  derniere_mise_a_jour: string;
  responsable: string;
  transporteur?: string;
  numero_tracking?: string;
  commentaires?: string;
}

interface FilterOptions {
  status: string;
  fournisseur: string;
  priorite: string;
  retard: string;
  dateDebut: string;
  dateFin: string;
}

const TableauSuiviCommandes: React.FC = () => {
  const [commandes, setCommandes] = useState<CommandeEnCours[]>([]);
  const [commandesFiltered, setCommandesFiltered] = useState<CommandeEnCours[]>([]);
  const [fournisseurs, setFournisseurs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    status: '',
    fournisseur: '',
    priorite: '',
    retard: '',
    dateDebut: '',
    dateFin: ''
  });
  const [sortBy, setSortBy] = useState<string>('date_commande');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedCommande, setSelectedCommande] = useState<CommandeEnCours | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [commandes, filters, sortBy, sortOrder]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Charger les commandes en cours
      const commandesData = await apiService.getCommandes({
        status: 'en_attente,approuvee,commandee',
        limit: 200
      });

      // Charger les fournisseurs
      const fournisseursResponse = await apiService.getFournisseurs({ limit: 100 });
      const fournisseursData = fournisseursResponse.fournisseurs || fournisseursResponse;
      setFournisseurs(fournisseursData);

      // Transformer les données en format CommandeEnCours
      const commandesEnCours: CommandeEnCours[] = await Promise.all(
        commandesData.map(async (cmd: any) => {
          const fournisseur = fournisseursData.find((f: any) => f.id === cmd.fournisseur_id);
          
          // Calculer les métriques
          const dateCommande = new Date(cmd.date_commande || cmd.created_at);
          const dateLivraisonPrevue = new Date(cmd.date_livraison_prevue || dateCommande.getTime() + 14 * 24 * 60 * 60 * 1000);
          const maintenant = new Date();
          
          const retardJours = Math.max(0, Math.floor((maintenant.getTime() - dateLivraisonPrevue.getTime()) / (1000 * 60 * 60 * 24)));
          
          let priorite: 'normale' | 'urgent' | 'critique' = 'normale';
          if (retardJours > 7) priorite = 'critique';
          else if (retardJours > 3) priorite = 'urgent';
          
          // Calculer la progression basée sur le statut
          let progression = 0;
          switch (cmd.status) {
            case 'brouillon': progression = 10; break;
            case 'en_attente': progression = 25; break;
            case 'approuvee': progression = 50; break;
            case 'commandee': progression = 75; break;
            case 'livree': progression = 100; break;
            default: progression = 0;
          }

          // Générer les alertes
          const alertes: string[] = [];
          if (retardJours > 0) {
            alertes.push(`Retard de ${retardJours} jour(s)`);
          }
          if (cmd.total_ttc > 10000) {
            alertes.push('Commande importante (>10k€)');
          }

          return {
            id: cmd.id,
            numero_commande: cmd.numero_commande,
            fournisseur: {
              nom: fournisseur?.nom || 'Fournisseur inconnu',
              code_fournisseur: fournisseur?.code_fournisseur || 'N/A'
            },
            status: cmd.status,
            date_commande: dateCommande.toISOString(),
            date_livraison_prevue: dateLivraisonPrevue.toISOString(),
            date_livraison_reelle: cmd.date_livraison_reelle,
            total_ttc: cmd.total_ttc || 0,
            nb_articles: cmd.lignes?.length || 0,
            priorite,
            retard_jours: retardJours,
            progression,
            alertes,
            derniere_mise_a_jour: cmd.updated_at || cmd.created_at,
            responsable: cmd.created_by || 'N/A',
            transporteur: cmd.transporteur,
            numero_tracking: cmd.numero_tracking,
            commentaires: cmd.notes
          };
        })
      );

      setCommandes(commandesEnCours);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...commandes];

    // Appliquer les filtres
    if (filters.status) {
      filtered = filtered.filter(cmd => cmd.status === filters.status);
    }
    
    if (filters.fournisseur) {
      filtered = filtered.filter(cmd => cmd.fournisseur.nom.toLowerCase().includes(filters.fournisseur.toLowerCase()));
    }
    
    if (filters.priorite) {
      filtered = filtered.filter(cmd => cmd.priorite === filters.priorite);
    }
    
    if (filters.retard === 'avec_retard') {
      filtered = filtered.filter(cmd => cmd.retard_jours > 0);
    } else if (filters.retard === 'sans_retard') {
      filtered = filtered.filter(cmd => cmd.retard_jours === 0);
    }
    
    if (filters.dateDebut) {
      filtered = filtered.filter(cmd => new Date(cmd.date_commande) >= new Date(filters.dateDebut));
    }
    
    if (filters.dateFin) {
      filtered = filtered.filter(cmd => new Date(cmd.date_commande) <= new Date(filters.dateFin));
    }

    // Appliquer le tri
    filtered.sort((a, b) => {
      let aVal: any = a[sortBy as keyof CommandeEnCours];
      let bVal: any = b[sortBy as keyof CommandeEnCours];
      
      // Gestion spéciale pour les objets imbriqués
      if (sortBy === 'fournisseur') {
        aVal = a.fournisseur.nom;
        bVal = b.fournisseur.nom;
      }
      
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    setCommandesFiltered(filtered);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'brouillon': { color: 'bg-gray-100 text-gray-800', label: 'Brouillon' },
      'en_attente': { color: 'bg-yellow-100 text-yellow-800', label: 'En attente' },
      'approuvee': { color: 'bg-blue-100 text-blue-800', label: 'Approuvée' },
      'commandee': { color: 'bg-purple-100 text-purple-800', label: 'Commandée' },
      'livree': { color: 'bg-green-100 text-green-800', label: 'Livrée' },
      'annulee': { color: 'bg-red-100 text-red-800', label: 'Annulée' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.brouillon;
    
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const getPriorityBadge = (priorite: string, retardJours: number) => {
    const priorityConfig = {
      'normale': { color: 'bg-green-100 text-green-800', icon: CheckCircleIcon },
      'urgent': { color: 'bg-yellow-100 text-yellow-800', icon: ExclamationTriangleIcon },
      'critique': { color: 'bg-red-100 text-red-800', icon: ExclamationTriangleIcon }
    };
    
    const config = priorityConfig[priorite as keyof typeof priorityConfig];
    const IconComponent = config.icon;
    
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full items-center space-x-1 ${config.color}`}>
        <IconComponent className="h-3 w-3" />
        <span>{priorite}</span>
        {retardJours > 0 && <span>({retardJours}j)</span>}
      </span>
    );
  };

  const openModal = (commande: CommandeEnCours) => {
    setSelectedCommande(commande);
    setShowModal(true);
  };

  const closeModal = () => {
    setSelectedCommande(null);
    setShowModal(false);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
      {/* En-tête */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Tableau de suivi des commandes en cours
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Suivi temps réel avec alertes de retard et niveaux de priorité
            </p>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={loadData}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700"
            >
              <ArrowPathIcon className="w-5 h-5" />
              <span>Actualiser</span>
            </button>
          </div>
        </div>

        {/* Filtres */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-6 gap-4">
          <div>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous les statuts</option>
              <option value="en_attente">En attente</option>
              <option value="approuvee">Approuvée</option>
              <option value="commandee">Commandée</option>
            </select>
          </div>
          
          <div>
            <input
              type="text"
              placeholder="Fournisseur..."
              value={filters.fournisseur}
              onChange={(e) => setFilters({ ...filters, fournisseur: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <select
              value={filters.priorite}
              onChange={(e) => setFilters({ ...filters, priorite: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Toutes priorités</option>
              <option value="normale">Normale</option>
              <option value="urgent">Urgent</option>
              <option value="critique">Critique</option>
            </select>
          </div>
          
          <div>
            <select
              value={filters.retard}
              onChange={(e) => setFilters({ ...filters, retard: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous retards</option>
              <option value="avec_retard">Avec retard</option>
              <option value="sans_retard">Sans retard</option>
            </select>
          </div>
          
          <div>
            <input
              type="date"
              value={filters.dateDebut}
              onChange={(e) => setFilters({ ...filters, dateDebut: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <input
              type="date"
              value={filters.dateFin}
              onChange={(e) => setFilters({ ...filters, dateFin: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Statistiques rapides */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
            <div className="text-sm font-medium text-blue-900 dark:text-blue-100">Total commandes</div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{commandesFiltered.length}</div>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
            <div className="text-sm font-medium text-red-900 dark:text-red-100">En retard</div>
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {commandesFiltered.filter(cmd => cmd.retard_jours > 0).length}
            </div>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg">
            <div className="text-sm font-medium text-yellow-900 dark:text-yellow-100">Priorité urgente</div>
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {commandesFiltered.filter(cmd => cmd.priorite === 'urgent' || cmd.priorite === 'critique').length}
            </div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
            <div className="text-sm font-medium text-green-900 dark:text-green-100">Valeur totale</div>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {commandesFiltered.reduce((sum, cmd) => sum + cmd.total_ttc, 0).toLocaleString()}€
            </div>
          </div>
        </div>
      </div>

      {/* Tableau */}
      <div className="overflow-x-auto">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                  onClick={() => {
                    if (sortBy === 'numero_commande') {
                      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                    } else {
                      setSortBy('numero_commande');
                      setSortOrder('asc');
                    }
                  }}
                >
                  N° Commande
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                  onClick={() => {
                    if (sortBy === 'fournisseur') {
                      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                    } else {
                      setSortBy('fournisseur');
                      setSortOrder('asc');
                    }
                  }}
                >
                  Fournisseur
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Statut</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Dates</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Montant</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Priorité</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Progression</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Alertes</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {commandesFiltered.map((commande) => (
                <tr key={commande.id} className={`hover:bg-gray-50 dark:hover:bg-gray-700 ${commande.priorite === 'critique' ? 'bg-red-50 dark:bg-red-900/20' : commande.priorite === 'urgent' ? 'bg-yellow-50 dark:bg-yellow-900/20' : ''}`}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    {commande.numero_commande}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    <div className="flex flex-col">
                      <span className="font-medium">{commande.fournisseur.nom}</span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">{commande.fournisseur.code_fournisseur}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(commande.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    <div className="flex flex-col">
                      <span>Cmd: {new Date(commande.date_commande).toLocaleDateString('fr-FR')}</span>
                      <span className={`text-xs ${commande.retard_jours > 0 ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-500 dark:text-gray-400'}`}>
                        Prév: {new Date(commande.date_livraison_prevue).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    <div className="flex flex-col">
                      <span className="font-medium">{commande.total_ttc.toLocaleString()}€</span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">{commande.nb_articles} articles</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getPriorityBadge(commande.priorite, commande.retard_jours)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                        <div 
                          className={`h-2 rounded-full ${
                            commande.progression === 100 ? 'bg-green-600' : 
                            commande.progression >= 75 ? 'bg-blue-600' : 
                            commande.progression >= 50 ? 'bg-yellow-600' : 'bg-gray-600'
                          }`}
                          style={{ width: `${commande.progression}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-600 dark:text-gray-400">{commande.progression}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {commande.alertes.length > 0 ? (
                      <div className="flex flex-col space-y-1">
                        {commande.alertes.slice(0, 2).map((alerte, index) => (
                          <span key={index} className="text-xs bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 px-2 py-1 rounded">
                            {alerte}
                          </span>
                        ))}
                        {commande.alertes.length > 2 && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">+{commande.alertes.length - 2} autres</span>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-green-600 dark:text-green-400">Aucune alerte</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    <button
                      onClick={() => openModal(commande)}
                      className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* État vide */}
      {!loading && commandesFiltered.length === 0 && (
        <div className="px-6 py-12 text-center">
          <ClockIcon className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            Aucune commande en cours trouvée avec les filtres appliqués.
          </p>
        </div>
      )}

      {/* Modal de détails */}
      {showModal && selectedCommande && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white dark:bg-gray-800">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Détails de la commande {selectedCommande.numero_commande}
                </h3>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Informations générales</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Fournisseur:</span> {selectedCommande.fournisseur.nom}</div>
                      <div><span className="font-medium">Statut:</span> {getStatusBadge(selectedCommande.status)}</div>
                      <div><span className="font-medium">Responsable:</span> {selectedCommande.responsable}</div>
                      <div><span className="font-medium">Total TTC:</span> {selectedCommande.total_ttc.toLocaleString()}€</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Dates et délais</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Date commande:</span> {new Date(selectedCommande.date_commande).toLocaleDateString('fr-FR')}</div>
                      <div><span className="font-medium">Livraison prévue:</span> {new Date(selectedCommande.date_livraison_prevue).toLocaleDateString('fr-FR')}</div>
                      <div><span className="font-medium">Retard:</span> {selectedCommande.retard_jours > 0 ? `${selectedCommande.retard_jours} jour(s)` : 'Aucun'}</div>
                      <div><span className="font-medium">Progression:</span> {selectedCommande.progression}%</div>
                    </div>
                  </div>
                </div>
                
                {selectedCommande.transporteur && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Transport</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="font-medium">Transporteur:</span> {selectedCommande.transporteur}</div>
                      {selectedCommande.numero_tracking && (
                        <div><span className="font-medium">N° tracking:</span> {selectedCommande.numero_tracking}</div>
                      )}
                    </div>
                  </div>
                )}
                
                {selectedCommande.alertes.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Alertes</h4>
                    <div className="space-y-1">
                      {selectedCommande.alertes.map((alerte, index) => (
                        <div key={index} className="text-sm bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 px-3 py-2 rounded">
                          {alerte}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {selectedCommande.commentaires && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Commentaires</h4>
                    <div className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-3 rounded">
                      {selectedCommande.commentaires}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex justify-end mt-6">
                <button
                  onClick={closeModal}
                  className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
                >
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TableauSuiviCommandes;