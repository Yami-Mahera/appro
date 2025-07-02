import React, { useState, useEffect } from 'react';
import { PlusIcon, PencilIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import ApiService from '../../services/api';

interface Article {
  id: string;
  nom: string;
  description: string;
  prix_unitaire: number;
  stock_actuel: number;
  stock_minimum: number;
  unite: string;
  famille: string;
  fournisseur_id: string;
  fournisseur_nom?: string;
  created_at: string;
}

interface Fournisseur {
  id: string;
  nom: string;
}

const Articles: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [filter, setFilter] = useState('');
  const [showStockBas, setShowStockBas] = useState(false);
  const [formData, setFormData] = useState({
    nom: '',
    description: '',
    prix_unitaire: '',
    stock_actuel: '',
    stock_minimum: '',
    unite: '',
    famille: '',
    fournisseur_id: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [articlesData, fournisseursData] = await Promise.all([
        ApiService.getArticles(),
        ApiService.getFournisseurs()
      ]);
      
      // Enrichir les articles avec le nom du fournisseur
      const enrichedArticles = articlesData.map((article: Article) => ({
        ...article,
        fournisseur_nom: fournisseursData.find((f: Fournisseur) => f.id === article.fournisseur_id)?.nom || 'Inconnu'
      }));
      
      setArticles(enrichedArticles);
      setFournisseurs(fournisseursData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        prix_unitaire: parseFloat(formData.prix_unitaire),
        stock_actuel: parseInt(formData.stock_actuel),
        stock_minimum: parseInt(formData.stock_minimum)
      };
      
      if (editingArticle) {
        await ApiService.updateArticle(editingArticle.id, data);
      } else {
        await ApiService.createArticle(data);
      }
      setShowModal(false);
      setEditingArticle(null);
      setFormData({
        nom: '', description: '', prix_unitaire: '', stock_actuel: '', 
        stock_minimum: '', unite: '', famille: '', fournisseur_id: ''
      });
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la sauvegarde');
    }
  };

  const handleEdit = (article: Article) => {
    setEditingArticle(article);
    setFormData({
      nom: article.nom,
      description: article.description,
      prix_unitaire: article.prix_unitaire.toString(),
      stock_actuel: article.stock_actuel.toString(),
      stock_minimum: article.stock_minimum.toString(),
      unite: article.unite,
      famille: article.famille,
      fournisseur_id: article.fournisseur_id
    });
    setShowModal(true);
  };

  const handleAdd = () => {
    setEditingArticle(null);
    setFormData({
      nom: '', description: '', prix_unitaire: '', stock_actuel: '', 
      stock_minimum: '', unite: '', famille: '', fournisseur_id: ''
    });
    setShowModal(true);
  };

  const filteredArticles = articles.filter(article => {
    const matchesFilter = article.nom.toLowerCase().includes(filter.toLowerCase()) ||
                         article.famille.toLowerCase().includes(filter.toLowerCase()) ||
                         (article.fournisseur_nom && article.fournisseur_nom.toLowerCase().includes(filter.toLowerCase()));
    
    if (showStockBas) {
      return matchesFilter && article.stock_actuel <= article.stock_minimum;
    }
    
    return matchesFilter;
  });

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
        <h1 className="text-2xl font-bold text-gray-900">Articles</h1>
        <button
          onClick={handleAdd}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Ajouter un article</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <input
              type="text"
              placeholder="Rechercher par nom, famille ou fournisseur..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="stockBas"
              checked={showStockBas}
              onChange={(e) => setShowStockBas(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="stockBas" className="text-sm text-gray-700">
              Stock bas uniquement
            </label>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Article
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fournisseur
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Prix
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stock
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Famille
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredArticles.map((article) => (
              <tr key={article.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{article.nom}</div>
                    <div className="text-sm text-gray-500">{article.description}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{article.fournisseur_nom}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {article.prix_unitaire.toFixed(2)}€ / {article.unite}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm text-gray-900">
                      {article.stock_actuel} / {article.stock_minimum} min
                    </div>
                    {article.stock_actuel <= article.stock_minimum && (
                      <ExclamationTriangleIcon className="w-5 h-5 text-red-500 ml-2" />
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {article.famille}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEdit(article)}
                    className="text-blue-600 hover:text-blue-900 flex items-center space-x-1"
                  >
                    <PencilIcon className="w-4 h-4" />
                    <span>Modifier</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredArticles.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">Aucun article trouvé</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingArticle ? 'Modifier l\'article' : 'Ajouter un article'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Nom</label>
                  <input
                    type="text"
                    value={formData.nom}
                    onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Famille</label>
                  <input
                    type="text"
                    value={formData.famille}
                    onChange={(e) => setFormData({ ...formData, famille: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Prix unitaire (€)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.prix_unitaire}
                    onChange={(e) => setFormData({ ...formData, prix_unitaire: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Unité</label>
                  <input
                    type="text"
                    value={formData.unite}
                    onChange={(e) => setFormData({ ...formData, unite: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="ex: pièce, kg, litre..."
                    required
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Stock actuel</label>
                  <input
                    type="number"
                    value={formData.stock_actuel}
                    onChange={(e) => setFormData({ ...formData, stock_actuel: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Stock minimum</label>
                  <input
                    type="number"
                    value={formData.stock_minimum}
                    onChange={(e) => setFormData({ ...formData, stock_minimum: e.target.value })}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Fournisseur</label>
                <select
                  value={formData.fournisseur_id}
                  onChange={(e) => setFormData({ ...formData, fournisseur_id: e.target.value })}
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
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingArticle ? 'Modifier' : 'Ajouter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Articles;