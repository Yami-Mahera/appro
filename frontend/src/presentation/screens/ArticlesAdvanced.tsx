import React, { useState, useEffect } from "react";
import {
  PlusIcon,
  PencilIcon,
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  EyeIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import ApiService from "../../services/api";
import { debounce } from "lodash";
import Pagination from "../components/Pagination";

interface Article {
  id: string;
  reference: string;
  nom: string;
  description?: string;
  famille?: string;
  fournisseur_id: string;
  prix_unitaire: number;
  unite: string;
  seuil_min: number;
  seuil_max: number;
  stock_actuel: number;
  duree_vie?: number;
  emplacement_stockage?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

interface Fournisseur {
  id: string;
  nom: string;
}

type SortField =
  | "nom"
  | "reference"
  | "famille"
  | "prix_unitaire"
  | "stock_actuel"
  | "created_at";
type SortOrder = "asc" | "desc";

const ArticlesAdvanced: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [viewingArticle, setViewingArticle] = useState<Article | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Search and filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<SortField>("nom");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");
  const [filters, setFilters] = useState({
    famille: "",
    fournisseur_id: "",
    stock_bas: false,
    active: true as boolean | undefined,
  });

  const [formData, setFormData] = useState({
    reference: "",
    nom: "",
    description: "",
    famille: "",
    fournisseur_id: "",
    prix_unitaire: "",
    unite: "",
    seuil_min: "",
    seuil_max: "",
    stock_actuel: "",
    duree_vie: "",
    emplacement_stockage: "",
  });

  useEffect(() => {
    loadFournisseurs();
  }, []);

  useEffect(() => {
    const debouncedLoad = debounce(() => {
      loadArticles();
    }, 300); // délai de 300ms

    debouncedLoad();

    // Nettoyage pour éviter des appels en cascade
    return () => debouncedLoad.cancel();
  }, [searchTerm, sortField, sortOrder, filters]);

  const loadFournisseurs = async () => {
    try {
      const data = await ApiService.getFournisseurs();
      setFournisseurs(data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Erreur lors du chargement des fournisseurs"
      );
    }
  };

  const loadArticles = async () => {
    try {
      setLoading(true);
      const params = {
        search: searchTerm || undefined,
        sort_by: sortField,
        sort_order: sortOrder,
        famille: filters.famille || undefined,
        fournisseur_id: filters.fournisseur_id || undefined,
        stock_bas: filters.stock_bas || undefined,
        active: filters.active,
      };

      const data = await ApiService.getArticles(params);
      setArticles(data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Erreur lors du chargement des articles"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        prix_unitaire: parseFloat(formData.prix_unitaire),
        seuil_min: parseInt(formData.seuil_min),
        seuil_max: parseInt(formData.seuil_max),
        stock_actuel: parseInt(formData.stock_actuel),
        duree_vie: formData.duree_vie
          ? parseInt(formData.duree_vie)
          : undefined,
      };

      if (editingArticle) {
        await ApiService.updateArticle(editingArticle.id, submitData);
      } else {
        await ApiService.createArticle(submitData);
      }
      setShowModal(false);
      setEditingArticle(null);
      resetForm();
      loadArticles();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors de la sauvegarde");
    }
  };

  const resetForm = () => {
    setFormData({
      reference: "",
      nom: "",
      description: "",
      famille: "",
      fournisseur_id: "",
      prix_unitaire: "",
      unite: "",
      seuil_min: "",
      seuil_max: "",
      stock_actuel: "",
      duree_vie: "",
      emplacement_stockage: "",
    });
  };

  const handleEdit = (article: Article) => {
    setEditingArticle(article);
    setFormData({
      reference: article.reference,
      nom: article.nom,
      description: article.description || "",
      famille: article.famille || "",
      fournisseur_id: article.fournisseur_id,
      prix_unitaire: article.prix_unitaire.toString(),
      unite: article.unite,
      seuil_min: article.seuil_min.toString(),
      seuil_max: article.seuil_max.toString(),
      stock_actuel: article.stock_actuel.toString(),
      duree_vie: article.duree_vie?.toString() || "",
      emplacement_stockage: article.emplacement_stockage || "",
    });
    setShowModal(true);
  };

  const handleView = (article: Article) => {
    setViewingArticle(article);
    setShowDetailModal(true);
  };

  const handleAdd = () => {
    setEditingArticle(null);
    resetForm();
    setShowModal(true);
  };

  const getFournisseurNom = (fournisseurId: string) => {
    const fournisseur = fournisseurs.find((f) => f.id === fournisseurId);
    return fournisseur ? fournisseur.nom : "Inconnu";
  };

  const getStockStatus = (article: Article) => {
    if (article.stock_actuel <= article.seuil_min) {
      return { status: "critique", color: "text-red-600", bg: "bg-red-100" };
    } else if (article.stock_actuel <= article.seuil_min * 1.5) {
      return { status: "bas", color: "text-orange-600", bg: "bg-orange-100" };
    } else {
      return { status: "normal", color: "text-green-600", bg: "bg-green-100" };
    }
  };

  const SortableHeader = ({
    field,
    children,
  }: {
    field: SortField;
    children: React.ReactNode;
  }) => (
    <th
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortField === field &&
          (sortOrder === "asc" ? (
            <ChevronUpIcon className="w-4 h-4" />
          ) : (
            <ChevronDownIcon className="w-4 h-4" />
          ))}
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Articles</h1>
        <button
          onClick={handleAdd}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Ajouter un article</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded dark:bg-red-900 dark:border-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
        <div className="flex flex-col md:flex-row gap-4 items-center">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par nom, référence, famille, description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300"
          >
            <AdjustmentsHorizontalIcon className="w-5 h-5" />
            <span>Filtres</span>
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Famille
              </label>
              <input
                type="text"
                value={filters.famille}
                onChange={(e) =>
                  setFilters({ ...filters, famille: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                placeholder="Filtrer par famille"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Fournisseur
              </label>
              <select
                value={filters.fournisseur_id}
                onChange={(e) =>
                  setFilters({ ...filters, fournisseur_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="">Tous les fournisseurs</option>
                {fournisseurs.map((fournisseur) => (
                  <option key={fournisseur.id} value={fournisseur.id}>
                    {fournisseur.nom}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center pt-6">
              <input
                type="checkbox"
                id="stockBas"
                checked={filters.stock_bas}
                onChange={(e) =>
                  setFilters({ ...filters, stock_bas: e.target.checked })
                }
                className="mr-2"
              />
              <label htmlFor="stockBas" className="text-sm text-gray-700 dark:text-gray-300">
                Stock bas uniquement
              </label>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Statut
              </label>
              <select
                value={
                  filters.active === undefined
                    ? "all"
                    : filters.active.toString()
                }
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    active:
                      e.target.value === "all"
                        ? undefined
                        : e.target.value === "true",
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="all">Tous</option>
                <option value="true">Actifs</option>
                <option value="false">Inactifs</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <SortableHeader field="reference">Référence</SortableHeader>
                <SortableHeader field="nom">Nom</SortableHeader>
                <SortableHeader field="famille">Famille</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Fournisseur
                </th>
                <SortableHeader field="prix_unitaire">Prix</SortableHeader>
                <SortableHeader field="stock_actuel">Stock</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Statut
                </th>
                <SortableHeader field="created_at">Créé le</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {articles.map((article) => {
                const stockStatus = getStockStatus(article);
                return (
                  <tr key={article.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                        {article.reference}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {article.nom}
                        </div>
                        {article.description && (
                          <div className="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
                            {article.description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {article.famille && (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                          {article.famille}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {getFournisseurNom(article.fournisseur_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {article.prix_unitaire.toFixed(2)}€ / {article.unite}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-sm text-gray-900 dark:text-gray-100">
                          {article.stock_actuel} / {article.seuil_min} min
                        </span>
                        {article.stock_actuel <= article.seuil_min && (
                          <ExclamationTriangleIcon className="w-5 h-5 text-red-500 ml-2" />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${stockStatus.bg} ${stockStatus.color}`}
                      >
                        {stockStatus.status.charAt(0).toUpperCase() +
                          stockStatus.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(article.created_at).toLocaleDateString("fr-FR")}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleView(article)}
                          className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                          title="Voir les détails"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(article)}
                          className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                          title="Modifier"
                        >
                          <PencilIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {articles.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">Aucun article trouvé</p>
          </div>
        )}
      </div>

      {/* Edit/Add Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingArticle ? "Modifier l'article" : "Ajouter un article"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Référence *
                  </label>
                  <input
                    type="text"
                    value={formData.reference}
                    onChange={(e) =>
                      setFormData({ ...formData, reference: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Nom *
                  </label>
                  <input
                    type="text"
                    value={formData.nom}
                    onChange={(e) =>
                      setFormData({ ...formData, nom: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Famille
                  </label>
                  <input
                    type="text"
                    value={formData.famille}
                    onChange={(e) =>
                      setFormData({ ...formData, famille: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Fournisseur *
                  </label>
                  <select
                    value={formData.fournisseur_id}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        fournisseur_id: e.target.value,
                      })
                    }
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
              </div>

              {/* Price and Unit */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Prix unitaire (€) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.prix_unitaire}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        prix_unitaire: e.target.value,
                      })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Unité *
                  </label>
                  <input
                    type="text"
                    value={formData.unite}
                    onChange={(e) =>
                      setFormData({ ...formData, unite: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="ex: pièce, kg, litre..."
                    required
                  />
                </div>
              </div>

              {/* Stock */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Stock actuel *
                  </label>
                  <input
                    type="number"
                    value={formData.stock_actuel}
                    onChange={(e) =>
                      setFormData({ ...formData, stock_actuel: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Seuil minimum *
                  </label>
                  <input
                    type="number"
                    value={formData.seuil_min}
                    onChange={(e) =>
                      setFormData({ ...formData, seuil_min: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Seuil maximum *
                  </label>
                  <input
                    type="number"
                    value={formData.seuil_max}
                    onChange={(e) =>
                      setFormData({ ...formData, seuil_max: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>

              {/* Additional Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Durée de vie (jours)
                  </label>
                  <input
                    type="number"
                    value={formData.duree_vie}
                    onChange={(e) =>
                      setFormData({ ...formData, duree_vie: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Emplacement de stockage
                  </label>
                  <input
                    type="text"
                    value={formData.emplacement_stockage}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        emplacement_stockage: e.target.value,
                      })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="ex: Étagère A1, Zone B..."
                  />
                </div>
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
                  {editingArticle ? "Modifier" : "Ajouter"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && viewingArticle && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Détails de l'article</h2>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Référence:
                  </span>
                  <p className="text-gray-900">{viewingArticle.reference}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Nom:
                  </span>
                  <p className="text-gray-900">{viewingArticle.nom}</p>
                </div>
              </div>

              {viewingArticle.description && (
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Description:
                  </span>
                  <p className="text-gray-900">{viewingArticle.description}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Famille:
                  </span>
                  <p className="text-gray-900">
                    {viewingArticle.famille || "Non renseignée"}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Fournisseur:
                  </span>
                  <p className="text-gray-900">
                    {getFournisseurNom(viewingArticle.fournisseur_id)}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Prix unitaire:
                  </span>
                  <p className="text-gray-900">
                    {viewingArticle.prix_unitaire.toFixed(2)}€ /{" "}
                    {viewingArticle.unite}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Valeur stock:
                  </span>
                  <p className="text-gray-900">
                    {(
                      viewingArticle.prix_unitaire * viewingArticle.stock_actuel
                    ).toFixed(2)}
                    €
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Stock actuel:
                  </span>
                  <p className="text-gray-900">{viewingArticle.stock_actuel}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Seuil minimum:
                  </span>
                  <p className="text-gray-900">{viewingArticle.seuil_min}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Seuil maximum:
                  </span>
                  <p className="text-gray-900">{viewingArticle.seuil_max}</p>
                </div>
              </div>

              {viewingArticle.duree_vie && (
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Durée de vie:
                  </span>
                  <p className="text-gray-900">
                    {viewingArticle.duree_vie} jours
                  </p>
                </div>
              )}

              {viewingArticle.emplacement_stockage && (
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Emplacement de stockage:
                  </span>
                  <p className="text-gray-900">
                    {viewingArticle.emplacement_stockage}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                <div>
                  <span className="font-medium">Créé le:</span>
                  <p>
                    {new Date(viewingArticle.created_at).toLocaleDateString(
                      "fr-FR"
                    )}
                  </p>
                </div>
                <div>
                  <span className="font-medium">Modifié le:</span>
                  <p>
                    {new Date(viewingArticle.updated_at).toLocaleDateString(
                      "fr-FR"
                    )}
                  </p>
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-500">
                  Statut du stock:
                </span>
                <div className="mt-2">
                  {(() => {
                    const status = getStockStatus(viewingArticle);
                    return (
                      <span
                        className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${status.bg} ${status.color}`}
                      >
                        {status.status.charAt(0).toUpperCase() +
                          status.status.slice(1)}
                      </span>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArticlesAdvanced;
