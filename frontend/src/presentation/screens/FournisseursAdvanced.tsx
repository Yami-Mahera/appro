import React, { useState, useEffect } from 'react';
import { fournisseursAPI } from '../../services/api';
import type { Fournisseur, FournisseurCreate, Contact } from '../../common/types';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const FournisseursAdvanced: React.FC = () => {
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingFournisseur, setEditingFournisseur] = useState<Fournisseur | null>(null);
  const [formData, setFormData] = useState<FournisseurCreate>({
    nom: '',
    code_fournisseur: '',
    adresse: '',
    ville: '',
    code_postal: '',
    pays: 'France',
    telephone: '',
    email: '',
    site_web: '',
    conditions_paiement: '',
    delai_livraison_moyen: undefined,
    contacts: [],
  });

  useEffect(() => {
    loadFournisseurs();
  }, [searchTerm]);

  const loadFournisseurs = async () => {
    try {
      setLoading(true);
      const data = await fournisseursAPI.getAll({
        search: searchTerm || undefined,
        sort_by: 'nom',
        sort_order: 'asc',
      });
      setFournisseurs(data);
    } catch (error) {
      console.error('Error loading fournisseurs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingFournisseur) {
        await fournisseursAPI.update(editingFournisseur.id, formData);
      } else {
        await fournisseursAPI.create(formData);
      }
      setShowModal(false);
      resetForm();
      loadFournisseurs();
    } catch (error) {
      console.error('Error saving fournisseur:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      nom: '',
      code_fournisseur: '',
      adresse: '',
      ville: '',
      code_postal: '',
      pays: 'France',
      telephone: '',
      email: '',
      site_web: '',
      conditions_paiement: '',
      delai_livraison_moyen: undefined,
      contacts: [],
    });
    setEditingFournisseur(null);
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
      telephone: fournisseur.telephone || '',
      email: fournisseur.email || '',
      site_web: fournisseur.site_web || '',
      conditions_paiement: fournisseur.conditions_paiement || '',
      delai_livraison_moyen: fournisseur.delai_livraison_moyen,
      contacts: fournisseur.contacts,
    });
    setShowModal(true);
  };

  const addContact = () => {
    setFormData({
      ...formData,
      contacts: [
        ...(formData.contacts || []),
        { nom: '', prenom: '', telephone: '', email: '', poste: '' },
      ],
    });
  };

  const removeContact = (index: number) => {
    const newContacts = [...(formData.contacts || [])];
    newContacts.splice(index, 1);
    setFormData({ ...formData, contacts: newContacts });
  };

  const updateContact = (index: number, field: keyof Contact, value: string) => {
    const newContacts = [...(formData.contacts || [])];
    newContacts[index] = { ...newContacts[index], [field]: value };
    setFormData({ ...formData, contacts: newContacts });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Fournisseurs</h1>
          <p className="mt-2 text-sm text-gray-700">
            Gestion complète de vos fournisseurs et de leurs contacts.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            onClick={() => {
              resetForm();
              setShowModal(true);
            }}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            Nouveau fournisseur
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Rechercher un fournisseur..."
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Table */}
      <div className="mt-8 flow-root">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fournisseur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Localisation
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Délai livraison
                    </th>
                    <th className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {fournisseurs.map((fournisseur) => (
                    <tr key={fournisseur.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {fournisseur.nom}
                          </div>
                          <div className="text-sm text-gray-500">
                            {fournisseur.code_fournisseur}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {fournisseur.email || '-'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {fournisseur.telephone || '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {fournisseur.ville}
                        </div>
                        <div className="text-sm text-gray-500">
                          {fournisseur.pays}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {fournisseur.delai_livraison_moyen ? (
                          `${fournisseur.delai_livraison_moyen} jours`
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEdit(fournisseur)}
                          className="text-blue-600 hover:text-blue-900 mr-4"
                        >
                          <PencilIcon className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <form onSubmit={handleSubmit}>
                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {editingFournisseur ? 'Modifier' : 'Nouveau'} fournisseur
                    </h3>
                    <button
                      type="button"
                      onClick={() => setShowModal(false)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <XMarkIcon className="h-6 w-6" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Nom *
                      </label>
                      <input
                        type="text"
                        required
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.nom}
                        onChange={(e) =>
                          setFormData({ ...formData, nom: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Code fournisseur *
                      </label>
                      <input
                        type="text"
                        required
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.code_fournisseur}
                        onChange={(e) =>
                          setFormData({ ...formData, code_fournisseur: e.target.value })
                        }
                      />
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Adresse *
                      </label>
                      <input
                        type="text"
                        required
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.adresse}
                        onChange={(e) =>
                          setFormData({ ...formData, adresse: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Ville *
                      </label>
                      <input
                        type="text"
                        required
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.ville}
                        onChange={(e) =>
                          setFormData({ ...formData, ville: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Code postal *
                      </label>
                      <input
                        type="text"
                        required
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.code_postal}
                        onChange={(e) =>
                          setFormData({ ...formData, code_postal: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Pays *
                      </label>
                      <input
                        type="text"
                        required
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.pays}
                        onChange={(e) =>
                          setFormData({ ...formData, pays: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Téléphone
                      </label>
                      <input
                        type="text"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.telephone}
                        onChange={(e) =>
                          setFormData({ ...formData, telephone: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Email
                      </label>
                      <input
                        type="email"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.email}
                        onChange={(e) =>
                          setFormData({ ...formData, email: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Site web
                      </label>
                      <input
                        type="url"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.site_web}
                        onChange={(e) =>
                          setFormData({ ...formData, site_web: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Délai livraison moyen (jours)
                      </label>
                      <input
                        type="number"
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.delai_livraison_moyen || ''}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            delai_livraison_moyen: e.target.value ? parseInt(e.target.value) : undefined,
                          })
                        }
                      />
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Conditions de paiement
                      </label>
                      <textarea
                        rows={3}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={formData.conditions_paiement}
                        onChange={(e) =>
                          setFormData({ ...formData, conditions_paiement: e.target.value })
                        }
                      />
                    </div>
                  </div>

                  {/* Contacts Section */}
                  <div className="mt-6">
                    <div className="flex items-center justify-between">
                      <h4 className="text-md font-medium text-gray-900">Contacts</h4>
                      <button
                        type="button"
                        onClick={addContact}
                        className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                      >
                        <PlusIcon className="h-4 w-4 mr-1" />
                        Ajouter contact
                      </button>
                    </div>

                    {formData.contacts?.map((contact, index) => (
                      <div key={index} className="mt-4 p-4 border rounded-lg">
                        <div className="flex justify-between items-start mb-3">
                          <h5 className="text-sm font-medium text-gray-700">
                            Contact {index + 1}
                          </h5>
                          <button
                            type="button"
                            onClick={() => removeContact(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                          <div>
                            <label className="block text-sm font-medium text-gray-700">
                              Nom
                            </label>
                            <input
                              type="text"
                              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                              value={contact.nom}
                              onChange={(e) =>
                                updateContact(index, 'nom', e.target.value)
                              }
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700">
                              Prénom
                            </label>
                            <input
                              type="text"
                              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                              value={contact.prenom}
                              onChange={(e) =>
                                updateContact(index, 'prenom', e.target.value)
                              }
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700">
                              Téléphone
                            </label>
                            <input
                              type="text"
                              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                              value={contact.telephone || ''}
                              onChange={(e) =>
                                updateContact(index, 'telephone', e.target.value)
                              }
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700">
                              Email
                            </label>
                            <input
                              type="email"
                              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                              value={contact.email || ''}
                              onChange={(e) =>
                                updateContact(index, 'email', e.target.value)
                              }
                            />
                          </div>
                          <div className="sm:col-span-2">
                            <label className="block text-sm font-medium text-gray-700">
                              Poste
                            </label>
                            <input
                              type="text"
                              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                              value={contact.poste || ''}
                              onChange={(e) =>
                                updateContact(index, 'poste', e.target.value)
                              }
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                  <button
                    type="submit"
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  >
                    {editingFournisseur ? 'Modifier' : 'Créer'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FournisseursAdvanced;