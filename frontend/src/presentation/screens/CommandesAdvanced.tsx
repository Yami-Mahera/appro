import React, { useState, useEffect } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  EyeIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import ApiService from '../../services/api';

interface LigneCommande {
  article_id: string;
  quantite: number;
  prix_unitaire: number;
  total: number;
}

interface Commande {
  id: string;
  numero_commande: string;
  fournisseur_id: string;
  status: string;
  lignes: LigneCommande[];
  total_ht: number;
  total_ttc: number;
  taux_tva: number;
  date_commande?: string;
  date_livraison_prevue?: string;
  date_livraison_reelle?: string;
  notes?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface CommandesResponse {
  commandes: Commande[];
  total: number;
  limit: number;
  skip: number;
  has_next: boolean;
  has_previous: boolean;
}

interface Article {
  id: string;
  reference: string;
  nom: string;
  prix_unitaire: number;
  unite: string;
  stock_actuel: number;
  fournisseur_id: string;
}

interface Fournisseur {
  id: string;
  nom: string;
}

type SortField = 'numero_commande' | 'status' | 'total_ttc' | 'created_at' | 'date_livraison_prevue';
type SortOrder = 'asc' | 'desc';

const STATUS_OPTIONS = [
  { value: 'brouillon', label: 'Brouillon', color: 'bg-gray-100 text-gray-800' },
  { value: 'en_attente', label: 'En attente', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'approuvee', label: 'Approuvée', color: 'bg-blue-100 text-blue-800' },
  { value: 'commandee', label: 'Commandée', color: 'bg-purple-100 text-purple-800' },
  { value: 'livree', label: 'Livrée', color: 'bg-green-100 text-green-800' },
  { value: 'annulee', label: 'Annulée', color: 'bg-red-100 text-red-800' }
];

const CommandesAdvanced: React.FC = () => {
  const [commandes, setCommandes] = useState<Commande[]>([]);
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingCommande, setEditingCommande] = useState<Commande | null>(null);
  const [viewingCommande, setViewingCommande] = useState<Commande | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filters, setFilters] = useState({
    status: '',
    fournisseur_id: '',
    date_from: '',
    date_to: ''
  });

  const [formData, setFormData] = useState({
    fournisseur_id: '',
    lignes: [] as LigneCommande[],
    date_livraison_prevue: '',
    notes: ''
  });

  const [newLigne, setNewLigne] = useState({
    article_id: '',
    quantite: 1
  });

  useEffect(() => {
    loadFournisseurs();
    loadArticles();
  }, []);

  useEffect(() => {
    loadCommandes();
  }, [searchTerm, sortField, sortOrder, filters]);

  const loadFournisseurs = async () => {
    try {
      const response = await ApiService.getFournisseurs();
      const data = response.fournisseurs || response;
      setFournisseurs(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement des fournisseurs');
    }
  };

  const loadArticles = async () => {
    try {
      const response = await ApiService.getArticles();
      const data = response.articles || response;
      setArticles(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement des articles');
    }
  };

  const loadCommandes = async () => {
    try {
      setLoading(true);
      const params = {
        search: searchTerm || undefined,
        sort_by: sortField,
        sort_order: sortOrder,
        status: filters.status || undefined,
        fournisseur_id: filters.fournisseur_id || undefined,
        date_from: filters.date_from || undefined,
        date_to: filters.date_to || undefined
      };
      
      const data = await ApiService.getCommandes(params);
      setCommandes(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement des commandes');
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        date_livraison_prevue: formData.date_livraison_prevue ? new Date(formData.date_livraison_prevue).toISOString() : undefined
      };

      if (editingCommande) {
        await ApiService.updateCommande(editingCommande.id, submitData);
      } else {
        await ApiService.createCommande(submitData);
      }
      setShowModal(false);
      setEditingCommande(null);
      resetForm();
      loadCommandes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde');
    }
  };

  const resetForm = () => {
    setFormData({
      fournisseur_id: '',
      lignes: [],
      date_livraison_prevue: '',
      notes: ''
    });
    setNewLigne({
      article_id: '',
      quantite: 1
    });
  };

  const handleView = (commande: Commande) => {
    setViewingCommande(commande);
    setShowDetailModal(true);
  };

  const handleAdd = () => {
    setEditingCommande(null);
    resetForm();
    setShowModal(true);
  };

  const addLigneCommande = () => {
    if (!newLigne.article_id) return;
    
    const article = articles.find(a => a.id === newLigne.article_id);
    if (!article) return;

    const existingIndex = formData.lignes.findIndex(l => l.article_id === newLigne.article_id);
    
    if (existingIndex >= 0) {
      // Update existing line
      const updatedLignes = [...formData.lignes];
      updatedLignes[existingIndex].quantite += newLigne.quantite;
      updatedLignes[existingIndex].total = updatedLignes[existingIndex].quantite * article.prix_unitaire;
      setFormData({ ...formData, lignes: updatedLignes });
    } else {
      // Add new line
      const nouvelleLigne: LigneCommande = {
        article_id: newLigne.article_id,
        quantite: newLigne.quantite,
        prix_unitaire: article.prix_unitaire,
        total: newLigne.quantite * article.prix_unitaire
      };
      setFormData({ ...formData, lignes: [...formData.lignes, nouvelleLigne] });
    }

    setNewLigne({ article_id: '', quantite: 1 });
  };

  const removeLigneCommande = (index: number) => {
    const updatedLignes = formData.lignes.filter((_, i) => i !== index);
    setFormData({ ...formData, lignes: updatedLignes });
  };

  const updateQuantite = (index: number, quantite: number) => {
    const updatedLignes = [...formData.lignes];
    updatedLignes[index].quantite = quantite;
    updatedLignes[index].total = quantite * updatedLignes[index].prix_unitaire;
    setFormData({ ...formData, lignes: updatedLignes });
  };

  const getArticlesFournisseur = () => {
    if (!formData.fournisseur_id) return [];
    return articles.filter(a => a.fournisseur_id === formData.fournisseur_id);
  };

  const getFournisseurNom = (fournisseurId: string) => {
    const fournisseur = fournisseurs.find(f => f.id === fournisseurId);
    return fournisseur ? fournisseur.nom : 'Inconnu';
  };

  const getArticleNom = (articleId: string) => {
    const article = articles.find(a => a.id === articleId);
    return article ? `${article.reference} - ${article.nom}` : 'Inconnu';
  };

  const getStatusLabel = (status: string) => {
    const statusOption = STATUS_OPTIONS.find(s => s.value === status);
    return statusOption ? statusOption.label : status;
  };

  const getStatusColor = (status: string) => {
    const statusOption = STATUS_OPTIONS.find(s => s.value === status);
    return statusOption ? statusOption.color : 'bg-gray-100 text-gray-800';
  };

  const getTotalCommande = () => {
    return formData.lignes.reduce((sum, ligne) => sum + ligne.total, 0);
  };

  const SortableHeader = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <th 
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortField === field && (
          sortOrder === 'asc' ? <ChevronUpIcon className="w-4 h-4" /> : <ChevronDownIcon className="w-4 h-4" />
        )}
      </div>
    </th>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Commandes</h1>
        <button
          onClick={handleAdd}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Nouvelle commande</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm space-y-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64 relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Rechercher par numéro de commande, notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
          >
            <AdjustmentsHorizontalIcon className="w-5 h-5" />
            <span>Filtres</span>
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-600">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Statut</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Tous les statuts</option>
                {STATUS_OPTIONS.map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fournisseur</label>
              <select
                value={filters.fournisseur_id}
                onChange={(e) => setFilters({ ...filters, fournisseur_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Tous les fournisseurs</option>
                {fournisseurs.map((fournisseur) => (
                  <option key={fournisseur.id} value={fournisseur.id}>
                    {fournisseur.nom}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date début</label>
              <input
                type="date"
                value={filters.date_from}
                onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date fin</label>
              <input
                type="date"
                value={filters.date_to}
                onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <SortableHeader field="numero_commande">N° Commande</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fournisseur
                </th>
                <SortableHeader field="status">Statut</SortableHeader>
                <SortableHeader field="total_ttc">Total TTC</SortableHeader>
                <SortableHeader field="date_livraison_prevue">Livraison prévue</SortableHeader>
                <SortableHeader field="created_at">Créée le</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {commandes.map((commande) => (
                <tr key={commande.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900">{commande.numero_commande}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {getFournisseurNom(commande.fournisseur_id)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(commande.status)}`}>
                      {getStatusLabel(commande.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {commande.total_ttc.toFixed(2)}€
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {commande.date_livraison_prevue ? new Date(commande.date_livraison_prevue).toLocaleDateString('fr-FR') : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(commande.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleView(commande)}
                        className="text-green-600 hover:text-green-900"
                        title="Voir les détails"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setEditingCommande(commande)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Modifier"
                      >
                        <PencilIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {commandes.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">Aucune commande trouvée</p>
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingCommande ? 'Modifier la commande' : 'Nouvelle commande'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Fournisseur *</label>
                  <select
                    value={formData.fournisseur_id}
                    onChange={(e) => setFormData({ ...formData, fournisseur_id: e.target.value, lignes: [] })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="">Sélectionner un fournisseur</option>
                    {fournisseurs.map((fournisseur) => (
                      <option key={fournisseur.id} value={fournisseur.id}>
                        {fournisseur.nom}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Date de livraison prévue</label>
                  <input
                    type="date"
                    value={formData.date_livraison_prevue}
                    onChange={(e) => setFormData({ ...formData, date_livraison_prevue: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Articles Section */}
              {formData.fournisseur_id && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Articles à commander</h3>
                  
                  {/* Add Article Form */}
                  <div className="bg-gray-50 p-4 rounded-lg mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Article</label>
                        <select
                          value={newLigne.article_id}
                          onChange={(e) => setNewLigne({ ...newLigne, article_id: e.target.value })}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Sélectionner un article</option>
                          {getArticlesFournisseur().map((article) => (
                            <option key={article.id} value={article.id}>
                              {article.reference} - {article.nom} ({article.prix_unitaire.toFixed(2)}€)
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Quantité</label>
                        <input
                          type="number"
                          min="1"
                          value={newLigne.quantite}
                          onChange={(e) => setNewLigne({ ...newLigne, quantite: parseInt(e.target.value) || 1 })}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <button
                          type="button"
                          onClick={addLigneCommande}
                          disabled={!newLigne.article_id}
                          className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-gray-300"
                        >
                          Ajouter
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Articles List */}
                  {formData.lignes.length > 0 && (
                    <div className="border border-gray-200 rounded-lg overflow-hidden">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Article</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix unitaire</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantité</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {formData.lignes.map((ligne, index) => (
                            <tr key={index}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {getArticleNom(ligne.article_id)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {ligne.prix_unitaire.toFixed(2)}€
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <input
                                  type="number"
                                  min="1"
                                  value={ligne.quantite}
                                  onChange={(e) => updateQuantite(index, parseInt(e.target.value) || 1)}
                                  className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                                />
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {ligne.total.toFixed(2)}€
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <button
                                  type="button"
                                  onClick={() => removeLigneCommande(index)}
                                  className="text-red-600 hover:text-red-900"
                                >
                                  <TrashIcon className="w-4 h-4" />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      
                      {/* Total */}
                      <div className="bg-gray-50 px-6 py-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">Total HT:</span>
                          <span className="text-sm font-semibold text-gray-900">{getTotalCommande().toFixed(2)}€</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">TVA (20%):</span>
                          <span className="text-sm font-semibold text-gray-900">{(getTotalCommande() * 0.2).toFixed(2)}€</span>
                        </div>
                        <div className="flex justify-between items-center border-t border-gray-200 pt-2 mt-2">
                          <span className="text-base font-semibold text-gray-900">Total TTC:</span>
                          <span className="text-base font-bold text-gray-900">{(getTotalCommande() * 1.2).toFixed(2)}€</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  placeholder="Notes ou commentaires sur la commande..."
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={formData.lignes.length === 0}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300"
                >
                  {editingCommande ? 'Modifier' : 'Créer la commande'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && viewingCommande && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Détails de la commande</h2>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Header Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">N° Commande:</span>
                  <p className="text-gray-900 font-semibold">{viewingCommande.numero_commande}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Fournisseur:</span>
                  <p className="text-gray-900">{getFournisseurNom(viewingCommande.fournisseur_id)}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Statut:</span>
                  <p>
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(viewingCommande.status)}`}>
                      {getStatusLabel(viewingCommande.status)}
                    </span>
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Date de création:</span>
                  <p className="text-gray-900">{new Date(viewingCommande.created_at).toLocaleDateString('fr-FR')}</p>
                </div>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Date commande:</span>
                  <p className="text-gray-900">
                    {viewingCommande.date_commande ? new Date(viewingCommande.date_commande).toLocaleDateString('fr-FR') : '-'}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Livraison prévue:</span>
                  <p className="text-gray-900">
                    {viewingCommande.date_livraison_prevue ? new Date(viewingCommande.date_livraison_prevue).toLocaleDateString('fr-FR') : '-'}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Livraison réelle:</span>
                  <p className="text-gray-900">
                    {viewingCommande.date_livraison_reelle ? new Date(viewingCommande.date_livraison_reelle).toLocaleDateString('fr-FR') : '-'}
                  </p>
                </div>
              </div>

              {/* Articles */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Articles commandés</h3>
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Article</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix unitaire</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantité</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {viewingCommande.lignes.map((ligne, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {getArticleNom(ligne.article_id)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {ligne.prix_unitaire.toFixed(2)}€
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {ligne.quantite}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {ligne.total.toFixed(2)}€
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {/* Totals */}
                  <div className="bg-gray-50 px-6 py-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Total HT:</span>
                      <span className="text-sm font-semibold text-gray-900">{viewingCommande.total_ht.toFixed(2)}€</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">TVA ({viewingCommande.taux_tva}%):</span>
                      <span className="text-sm font-semibold text-gray-900">{(viewingCommande.total_ttc - viewingCommande.total_ht).toFixed(2)}€</span>
                    </div>
                    <div className="flex justify-between items-center border-t border-gray-200 pt-2 mt-2">
                      <span className="text-base font-semibold text-gray-900">Total TTC:</span>
                      <span className="text-base font-bold text-gray-900">{viewingCommande.total_ttc.toFixed(2)}€</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Notes */}
              {viewingCommande.notes && (
                <div>
                  <span className="text-sm font-medium text-gray-500">Notes:</span>
                  <p className="text-gray-900 mt-1">{viewingCommande.notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommandesAdvanced;