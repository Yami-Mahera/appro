import React, { useState, useEffect } from "react";
import {
  PlusIcon,
  PencilIcon,
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  EyeIcon,
} from "@heroicons/react/24/outline";
import ApiService from "../../services/api";
import { debounce } from "lodash";
import Pagination from "../components/Pagination";

interface Contact {
  nom: string;
  prenom: string;
  telephone?: string;
  email?: string;
  poste?: string;
}

interface Fournisseur {
  id: string;
  nom: string;
  code_fournisseur: string;
  adresse: string;
  ville: string;
  code_postal: string;
  pays: string;
  telephone?: string;
  email?: string;
  site_web?: string;
  conditions_paiement?: string;
  delai_livraison_moyen?: number;
  contacts: Contact[];
  active: boolean;
  created_at: string;
  updated_at: string;
}

type SortField = "nom" | "ville" | "pays" | "created_at" | "code_fournisseur";
type SortOrder = "asc" | "desc";

const FournisseursAdvanced: React.FC = () => {
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingFournisseur, setEditingFournisseur] =
    useState<Fournisseur | null>(null);
  const [viewingFournisseur, setViewingFournisseur] =
    useState<Fournisseur | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Search and filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<SortField>("nom");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");
  const [filters, setFilters] = useState({
    ville: "",
    pays: "",
    active: true as boolean | undefined,
  });

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const [formData, setFormData] = useState({
    nom: "",
    code_fournisseur: "",
    adresse: "",
    ville: "",
    code_postal: "",
    pays: "France",
    telephone: "",
    email: "",
    site_web: "",
    conditions_paiement: "",
    delai_livraison_moyen: "",
    contacts: [] as Contact[],
  });

  useEffect(() => {
    const debouncedLoad = debounce(() => {
      loadFournisseurs();
    }, 300); // délai de 300ms

    debouncedLoad();

    // Nettoyage pour éviter des appels en cascade
    return () => debouncedLoad.cancel();
  }, [searchTerm, sortField, sortOrder, filters, currentPage, itemsPerPage]);

  const loadFournisseurs = async () => {
    try {
      setLoading(true);
      const skip = (currentPage - 1) * itemsPerPage;
      
      const params = {
        search: searchTerm || undefined,
        sort_by: sortField,
        sort_order: sortOrder,
        ville: filters.ville || undefined,
        pays: filters.pays || undefined,
        active: filters.active,
        limit: itemsPerPage,
        skip: skip,
      };

      const response = await ApiService.getFournisseurs(params);
      
      // Handle response - it might return fournisseurs array directly or a response object
      let fournisseursData = response;
      let total = response.length;
      
      // If the API returns a paginated response with metadata
      if (response && typeof response === 'object' && !Array.isArray(response)) {
        fournisseursData = response.fournisseurs || response.data || response;
        total = response.total || response.count || fournisseursData.length;
      }
      
      // If we got fewer items than requested and it's the first page, use the actual count
      if (currentPage === 1 && fournisseursData.length < itemsPerPage) {
        total = fournisseursData.length;
      }
      
      // Estimate total if not provided
      if (!total || total < skip + fournisseursData.length) {
        total = skip + fournisseursData.length + (fournisseursData.length === itemsPerPage ? itemsPerPage : 0);
      }
      
      setFournisseurs(fournisseursData);
      setTotalItems(total);
      setTotalPages(Math.ceil(total / itemsPerPage));
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Erreur lors du chargement des fournisseurs"
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
    setCurrentPage(1); // Reset to first page when sorting
  };

  // Pagination handlers
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleItemsPerPageChange = (newItemsPerPage: number) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1); // Reset to first page when changing items per page
  };

  // Reset to first page when filters change
  const handleFiltersChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handleSearchChange = (newSearchTerm: string) => {
    setSearchTerm(newSearchTerm);
    setCurrentPage(1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        delai_livraison_moyen: formData.delai_livraison_moyen
          ? parseInt(formData.delai_livraison_moyen)
          : undefined,
      };

      if (editingFournisseur) {
        await ApiService.updateFournisseur(editingFournisseur.id, submitData);
      } else {
        await ApiService.createFournisseur(submitData);
      }
      setShowModal(false);
      setEditingFournisseur(null);
      resetForm();
      loadFournisseurs();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors de la sauvegarde");
    }
  };

  const resetForm = () => {
    setFormData({
      nom: "",
      code_fournisseur: "",
      adresse: "",
      ville: "",
      code_postal: "",
      pays: "France",
      telephone: "",
      email: "",
      site_web: "",
      conditions_paiement: "",
      delai_livraison_moyen: "",
      contacts: [],
    });
  };

  const handleEdit = (fournisseur: Fournisseur) => {
    setEditingFournisseur(fournisseur);
    setFormData({
      nom: fournisseur.nom,
      code_fournisseur: fournisseur.code_fournisseur,
      adresse: fournisseur.adresse,
      ville: fournisseur.ville,
      code_postal: fournisseur.code_postal,
      pays: fournisseur.pays,
      telephone: fournisseur.telephone || "",
      email: fournisseur.email || "",
      site_web: fournisseur.site_web || "",
      conditions_paiement: fournisseur.conditions_paiement || "",
      delai_livraison_moyen:
        fournisseur.delai_livraison_moyen?.toString() || "",
      contacts: fournisseur.contacts || [],
    });
    setShowModal(true);
  };

  const handleView = (fournisseur: Fournisseur) => {
    setViewingFournisseur(fournisseur);
    setShowDetailModal(true);
  };

  const handleAdd = () => {
    setEditingFournisseur(null);
    resetForm();
    setShowModal(true);
  };

  const addContact = () => {
    setFormData({
      ...formData,
      contacts: [
        ...formData.contacts,
        { nom: "", prenom: "", telephone: "", email: "", poste: "" },
      ],
    });
  };

  const removeContact = (index: number) => {
    setFormData({
      ...formData,
      contacts: formData.contacts.filter((_, i) => i !== index),
    });
  };

  const updateContact = (
    index: number,
    field: keyof Contact,
    value: string
  ) => {
    const updatedContacts = [...formData.contacts];
    updatedContacts[index] = { ...updatedContacts[index], [field]: value };
    setFormData({ ...formData, contacts: updatedContacts });
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Fournisseurs</h1>
        <button
          onClick={handleAdd}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Ajouter un fournisseur</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded dark:bg-red-900 dark:border-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm space-y-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64 relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par nom, code, ville, email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300"
          >
            <AdjustmentsHorizontalIcon className="w-5 h-5" />
            <span>Filtres</span>
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Ville
              </label>
              <input
                type="text"
                value={filters.ville}
                onChange={(e) =>
                  setFilters({ ...filters, ville: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="Filtrer par ville"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Pays
              </label>
              <input
                type="text"
                value={filters.pays}
                onChange={(e) =>
                  setFilters({ ...filters, pays: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="Filtrer par pays"
              />
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
                <SortableHeader field="nom">Nom</SortableHeader>
                <SortableHeader field="code_fournisseur">Code</SortableHeader>
                <SortableHeader field="ville">Ville</SortableHeader>
                <SortableHeader field="pays">Pays</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Contact
                </th>
                <SortableHeader field="created_at">Créé le</SortableHeader>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {fournisseurs.map((fournisseur) => (
                <tr key={fournisseur.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {fournisseur.nom}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {fournisseur.email}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                      {fournisseur.code_fournisseur}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {fournisseur.ville}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {fournisseur.pays}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {fournisseur.telephone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {new Date(fournisseur.created_at).toLocaleDateString(
                      "fr-FR"
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleView(fournisseur)}
                        className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                        title="Voir les détails"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleEdit(fournisseur)}
                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
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

        {fournisseurs.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">Aucun fournisseur trouvé</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalItems > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={handlePageChange}
          onItemsPerPageChange={handleItemsPerPageChange}
        />
      )}

      {/* Edit/Add Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
              {editingFournisseur
                ? "Modifier le fournisseur"
                : "Ajouter un fournisseur"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Nom *
                  </label>
                  <input
                    type="text"
                    value={formData.nom}
                    onChange={(e) =>
                      setFormData({ ...formData, nom: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Code fournisseur *
                  </label>
                  <input
                    type="text"
                    value={formData.code_fournisseur}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        code_fournisseur: e.target.value,
                      })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    required
                  />
                </div>
              </div>

              {/* Address */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Adresse *
                </label>
                <textarea
                  value={formData.adresse}
                  onChange={(e) =>
                    setFormData({ ...formData, adresse: e.target.value })
                  }
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  rows={3}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Ville *
                  </label>
                  <input
                    type="text"
                    value={formData.ville}
                    onChange={(e) =>
                      setFormData({ ...formData, ville: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Code postal *
                  </label>
                  <input
                    type="text"
                    value={formData.code_postal}
                    onChange={(e) =>
                      setFormData({ ...formData, code_postal: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Pays *
                  </label>
                  <input
                    type="text"
                    value={formData.pays}
                    onChange={(e) =>
                      setFormData({ ...formData, pays: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    required
                  />
                </div>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    value={formData.telephone}
                    onChange={(e) =>
                      setFormData({ ...formData, telephone: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>

              {/* Business Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Site web
                  </label>
                  <input
                    type="url"
                    value={formData.site_web}
                    onChange={(e) =>
                      setFormData({ ...formData, site_web: e.target.value })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Délai livraison moyen (jours)
                  </label>
                  <input
                    type="number"
                    value={formData.delai_livraison_moyen}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        delai_livraison_moyen: e.target.value,
                      })
                    }
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Conditions de paiement
                </label>
                <textarea
                  value={formData.conditions_paiement}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      conditions_paiement: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  rows={2}
                />
              </div>

              {/* Contacts */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Contacts
                  </label>
                  <button
                    type="button"
                    onClick={addContact}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    + Ajouter un contact
                  </button>
                </div>
                {formData.contacts.map((contact, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 mb-3"
                  >
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-sm font-medium text-gray-700">
                        Contact {index + 1}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeContact(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Supprimer
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <input
                        type="text"
                        placeholder="Nom"
                        value={contact.nom}
                        onChange={(e) =>
                          updateContact(index, "nom", e.target.value)
                        }
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <input
                        type="text"
                        placeholder="Prénom"
                        value={contact.prenom}
                        onChange={(e) =>
                          updateContact(index, "prenom", e.target.value)
                        }
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <input
                        type="tel"
                        placeholder="Téléphone"
                        value={contact.telephone}
                        onChange={(e) =>
                          updateContact(index, "telephone", e.target.value)
                        }
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <input
                        type="email"
                        placeholder="Email"
                        value={contact.email}
                        onChange={(e) =>
                          updateContact(index, "email", e.target.value)
                        }
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <input
                        type="text"
                        placeholder="Poste"
                        value={contact.poste}
                        onChange={(e) =>
                          updateContact(index, "poste", e.target.value)
                        }
                        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 md:col-span-2"
                      />
                    </div>
                  </div>
                ))}
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
                  {editingFournisseur ? "Modifier" : "Ajouter"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && viewingFournisseur && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Détails du fournisseur</h2>
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
                    Nom:
                  </span>
                  <p className="text-gray-900">{viewingFournisseur.nom}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Code:
                  </span>
                  <p className="text-gray-900">
                    {viewingFournisseur.code_fournisseur}
                  </p>
                </div>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-500">
                  Adresse complète:
                </span>
                <p className="text-gray-900">
                  {viewingFournisseur.adresse}
                  <br />
                  {viewingFournisseur.code_postal} {viewingFournisseur.ville}
                  <br />
                  {viewingFournisseur.pays}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Téléphone:
                  </span>
                  <p className="text-gray-900">
                    {viewingFournisseur.telephone || "Non renseigné"}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Email:
                  </span>
                  <p className="text-gray-900">
                    {viewingFournisseur.email || "Non renseigné"}
                  </p>
                </div>
              </div>

              {viewingFournisseur.site_web && (
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Site web:
                  </span>
                  <p className="text-gray-900">
                    <a
                      href={viewingFournisseur.site_web}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {viewingFournisseur.site_web}
                    </a>
                  </p>
                </div>
              )}

              {viewingFournisseur.conditions_paiement && (
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Conditions de paiement:
                  </span>
                  <p className="text-gray-900">
                    {viewingFournisseur.conditions_paiement}
                  </p>
                </div>
              )}

              {viewingFournisseur.delai_livraison_moyen && (
                <div>
                  <span className="text-sm font-medium text-gray-500">
                    Délai de livraison moyen:
                  </span>
                  <p className="text-gray-900">
                    {viewingFournisseur.delai_livraison_moyen} jours
                  </p>
                </div>
              )}

              {viewingFournisseur.contacts &&
                viewingFournisseur.contacts.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-gray-500">
                      Contacts:
                    </span>
                    <div className="mt-2 space-y-2">
                      {viewingFournisseur.contacts.map((contact, index) => (
                        <div key={index} className="bg-gray-50 p-3 rounded">
                          <p className="font-medium">
                            {contact.prenom} {contact.nom}
                          </p>
                          {contact.poste && (
                            <p className="text-sm text-gray-600">
                              {contact.poste}
                            </p>
                          )}
                          {contact.telephone && (
                            <p className="text-sm">{contact.telephone}</p>
                          )}
                          {contact.email && (
                            <p className="text-sm">{contact.email}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                <div>
                  <span className="font-medium">Créé le:</span>
                  <p>
                    {new Date(viewingFournisseur.created_at).toLocaleDateString(
                      "fr-FR"
                    )}
                  </p>
                </div>
                <div>
                  <span className="font-medium">Modifié le:</span>
                  <p>
                    {new Date(viewingFournisseur.updated_at).toLocaleDateString(
                      "fr-FR"
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FournisseursAdvanced;
