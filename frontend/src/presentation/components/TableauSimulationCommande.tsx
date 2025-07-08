import React, { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon, CalculatorIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import apiService from '../../services/api';

interface LigneSimulation {
  id: string;
  articleId: string;
  designation: string;
  reference: string;
  quantite: number;
  prixUnitaire: number;
  total: number;
  cms: number;
  cmc: number;
  qm: number;
  stockActuel: number;
  couvertureActuelle: number;
  validation: {
    dateLimiteConsommation: boolean;
    espaceStockage: boolean;
    quantiteMin: boolean;
    delaiLivraison: boolean;
    stockSecurite: boolean;
    seuilSurstock: boolean;
  };
  recommandations: string[];
  status: 'valide' | 'attention' | 'erreur';
}

interface SimulationSummary {
  totalHT: number;
  totalTTC: number;
  nombreArticles: number;
  validationsReussies: number;
  alertes: string[];
}

const TableauSimulationCommande: React.FC = () => {
  const [lignes, setLignes] = useState<LigneSimulation[]>([]);
  const [articles, setArticles] = useState<any[]>([]);
  const [fournisseurs, setFournisseurs] = useState<any[]>([]);
  const [selectedFournisseur, setSelectedFournisseur] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [simulationSummary, setSimulationSummary] = useState<SimulationSummary>({
    totalHT: 0,
    totalTTC: 0,
    nombreArticles: 0,
    validationsReussies: 0,
    alertes: []
  });

  useEffect(() => {
    loadFournisseurs();
  }, []);

  useEffect(() => {
    if (selectedFournisseur) {
      loadArticlesByFournisseur();
    }
  }, [selectedFournisseur]);

  useEffect(() => {
    calculateSummary();
  }, [lignes]);

  const loadFournisseurs = async () => {
    try {
      const response = await apiService.getFournisseurs({ limit: 100 });
      const data = response.fournisseurs || response;
      setFournisseurs(data);
      if (data.length > 0 && !selectedFournisseur) {
        setSelectedFournisseur(data[0].id);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des fournisseurs:', error);
    }
  };

  const loadArticlesByFournisseur = async () => {
    try {
      const response = await apiService.getArticles({ 
        fournisseur_id: selectedFournisseur,
        limit: 100 
      });
      const data = response.articles || response;
      setArticles(data);
    } catch (error) {
      console.error('Erreur lors du chargement des articles:', error);
    }
  };

  const ajouterLigne = () => {
    if (articles.length === 0) return;

    const nouveauId = `temp-${Date.now()}`;
    const premierArticle = articles[0];
    
    const nouvelleLigne: LigneSimulation = {
      id: nouveauId,
      articleId: premierArticle.id,
      designation: premierArticle.nom,
      reference: premierArticle.reference,
      quantite: 1,
      prixUnitaire: premierArticle.prix_unitaire,
      total: premierArticle.prix_unitaire,
      cms: 0,
      cmc: 0,
      qm: 0,
      stockActuel: premierArticle.stock_actuel,
      couvertureActuelle: 0,
      validation: {
        dateLimiteConsommation: true,
        espaceStockage: true,
        quantiteMin: true,
        delaiLivraison: true,
        stockSecurite: true,
        seuilSurstock: true
      },
      recommandations: [],
      status: 'valide'
    };

    setLignes([...lignes, nouvelleLigne]);
    calculerMetriquesLigne(nouvelleLigne.id, premierArticle.id);
  };

  const supprimerLigne = (id: string) => {
    setLignes(lignes.filter(ligne => ligne.id !== id));
  };

  const mettreAJourLigne = (id: string, champ: keyof LigneSimulation, valeur: any) => {
    setLignes(lignes.map(ligne => {
      if (ligne.id === id) {
        const ligneModifiee = { ...ligne, [champ]: valeur };
        
        // Recalculer le total si quantité ou prix change
        if (champ === 'quantite' || champ === 'prixUnitaire') {
          ligneModifiee.total = ligneModifiee.quantite * ligneModifiee.prixUnitaire;
        }
        
        // Si l'article change, charger les nouvelles données
        if (champ === 'articleId') {
          const article = articles.find(a => a.id === valeur);
          if (article) {
            ligneModifiee.designation = article.nom;
            ligneModifiee.reference = article.reference;
            ligneModifiee.prixUnitaire = article.prix_unitaire;
            ligneModifiee.stockActuel = article.stock_actuel;
            ligneModifiee.total = ligneModifiee.quantite * article.prix_unitaire;
            
            // Calculer les métriques en arrière-plan
            setTimeout(() => calculerMetriquesLigne(id, valeur), 100);
          }
        }
        
        return ligneModifiee;
      }
      return ligne;
    }));
  };

  const calculerMetriquesLigne = async (ligneId: string, articleId: string) => {
    try {
      const couverture = await apiService.getCalculCouverture(articleId);
      
      setLignes(prevLignes => prevLignes.map(ligne => {
        if (ligne.id === ligneId) {
          return {
            ...ligne,
            cms: couverture.couverture_minimale_securite,
            cmc: couverture.couverture_maximale_commande,
            qm: couverture.quantite_maximale_commande,
            couvertureActuelle: couverture.couverture_actuelle
          };
        }
        return ligne;
      }));
      
      // Valider la ligne
      validerLigne(ligneId, articleId);
    } catch (error) {
      console.error('Erreur lors du calcul des métriques:', error);
    }
  };

  const validerLigne = async (ligneId: string, articleId: string) => {
    try {
      const ligne = lignes.find(l => l.id === ligneId);
      if (!ligne) return;

      const validationData = {
        article_id: articleId,
        quantite: ligne.quantite,
        date_livraison_prevue: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString() // +14 jours
      };

      const validation = await apiService.validateCommandeAvancee(validationData);
      
      setLignes(prevLignes => prevLignes.map(l => {
        if (l.id === ligneId) {
          const validationStatus = validation.validation_status === 'validee' ? 'valide' : 
                                 validation.recommandations.length > 0 ? 'attention' : 'erreur';
          
          return {
            ...l,
            validation: {
              dateLimiteConsommation: validation.date_limite_consommation,
              espaceStockage: validation.espace_stockage_disponible,
              quantiteMin: validation.quantite_min_respectee,
              delaiLivraison: validation.delai_livraison_acceptable,
              stockSecurite: validation.stock_securite_respecte,
              seuilSurstock: validation.seuil_surstock_respecte
            },
            recommandations: validation.recommandations || [],
            status: validationStatus
          };
        }
        return l;
      }));
    } catch (error) {
      console.error('Erreur lors de la validation:', error);
    }
  };

  const validerToutesLignes = () => {
    lignes.forEach(ligne => {
      validerLigne(ligne.id, ligne.articleId);
    });
  };

  const calculateSummary = () => {
    const totalHT = lignes.reduce((sum, ligne) => sum + ligne.total, 0);
    const totalTTC = totalHT * 1.2; // TVA 20%
    const nombreArticles = lignes.length;
    const validationsReussies = lignes.filter(ligne => ligne.status === 'valide').length;
    
    const alertes: string[] = [];
    lignes.forEach(ligne => {
      if (ligne.status === 'erreur') {
        alertes.push(`${ligne.reference}: Validation échouée`);
      } else if (ligne.status === 'attention') {
        alertes.push(`${ligne.reference}: Attention requise`);
      }
    });

    setSimulationSummary({
      totalHT,
      totalTTC,
      nombreArticles,
      validationsReussies,
      alertes
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'valide':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'attention':
        return <span className="h-5 w-5 text-yellow-500 text-center">⚠️</span>;
      case 'erreur':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getValidationBadge = (field: boolean, label: string) => (
    <span className={`px-2 py-1 text-xs rounded-full ${field ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
      {label}
    </span>
  );

  const selectedFournisseurData = fournisseurs.find(f => f.id === selectedFournisseur);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
      {/* En-tête */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Tableau de simulation de commande
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Simulation avancée avec validation des contraintes et calculs optimisés
            </p>
          </div>
          
          <div className="flex space-x-4">
            <div className="flex flex-col">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fournisseur</label>
              <select
                value={selectedFournisseur}
                onChange={(e) => setSelectedFournisseur(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Sélectionner un fournisseur</option>
                {fournisseurs.map((fournisseur) => (
                  <option key={fournisseur.id} value={fournisseur.id}>
                    {fournisseur.nom} - {fournisseur.code_fournisseur}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex space-x-2 items-end">
              <button
                onClick={ajouterLigne}
                disabled={!selectedFournisseur || articles.length === 0}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600"
              >
                <PlusIcon className="w-5 h-5" />
                <span>Ajouter ligne</span>
              </button>
              
              <button
                onClick={validerToutesLignes}
                disabled={lignes.length === 0}
                className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-green-700 disabled:bg-gray-300 dark:disabled:bg-gray-600"
              >
                <CalculatorIcon className="w-5 h-5" />
                <span>Valider tout</span>
              </button>
            </div>
          </div>
        </div>

        {/* Info fournisseur sélectionné */}
        {selectedFournisseurData && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Fournisseur:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedFournisseurData.nom}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Délai moyen:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedFournisseurData.delai_livraison_moyen || 'N/A'} jours</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Ville:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{selectedFournisseurData.ville}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">Articles disponibles:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{articles.length}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tableau de simulation */}
      <div className="overflow-x-auto">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Article</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Référence</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Quantité</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Prix Unit.</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Stock</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">CMS/CMC/QM</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Validation</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {lignes.map((ligne) => (
                <tr key={ligne.id} className={`hover:bg-gray-50 dark:hover:bg-gray-700 ${ligne.status === 'erreur' ? 'bg-red-50 dark:bg-red-900/20' : ligne.status === 'attention' ? 'bg-yellow-50 dark:bg-yellow-900/20' : ''}`}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={ligne.articleId}
                      onChange={(e) => mettreAJourLigne(ligne.id, 'articleId', e.target.value)}
                      className="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      {articles.map((article) => (
                        <option key={article.id} value={article.id}>
                          {article.nom}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    {ligne.reference}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="number"
                      min="1"
                      value={ligne.quantite}
                      onChange={(e) => mettreAJourLigne(ligne.id, 'quantite', parseInt(e.target.value) || 0)}
                      className="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {ligne.prixUnitaire.toFixed(2)}€
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    {ligne.total.toFixed(2)}€
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    <div className="flex flex-col">
                      <span>Actuel: {ligne.stockActuel}</span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Couv: {ligne.couvertureActuelle.toFixed(1)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    <div className="flex flex-col space-y-1 text-xs">
                      <span>CMS: {ligne.cms.toFixed(1)}</span>
                      <span>CMC: {ligne.cmc.toFixed(1)}</span>
                      <span className="font-medium text-blue-600 dark:text-blue-400">QM: {ligne.qm.toFixed(0)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(ligne.status)}
                      <div className="flex flex-wrap gap-1">
                        {getValidationBadge(ligne.validation.stockSecurite, 'Stock')}
                        {getValidationBadge(ligne.validation.quantiteMin, 'Qté')}
                        {getValidationBadge(ligne.validation.delaiLivraison, 'Délai')}
                      </div>
                    </div>
                    {ligne.recommandations.length > 0 && (
                      <div className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                        {ligne.recommandations.slice(0, 1).map((rec, idx) => (
                          <div key={idx}>{rec}</div>
                        ))}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => supprimerLigne(ligne.id)}
                      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Résumé de simulation */}
      {lignes.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700">Total HT</h4>
              <p className="text-2xl font-bold text-gray-900">{simulationSummary.totalHT.toFixed(2)}€</p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700">Total TTC</h4>
              <p className="text-2xl font-bold text-gray-900">{simulationSummary.totalTTC.toFixed(2)}€</p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700">Validations</h4>
              <p className="text-2xl font-bold text-gray-900">
                {simulationSummary.validationsReussies}/{simulationSummary.nombreArticles}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700">Alertes</h4>
              <p className="text-2xl font-bold text-red-600">{simulationSummary.alertes.length}</p>
            </div>
          </div>
          
          {simulationSummary.alertes.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Alertes détaillées:</h4>
              <div className="space-y-1">
                {simulationSummary.alertes.map((alerte, index) => (
                  <div key={index} className="text-sm text-red-600 bg-red-50 px-3 py-1 rounded">
                    {alerte}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* État vide */}
      {lignes.length === 0 && (
        <div className="px-6 py-12 text-center">
          <p className="text-gray-500">
            Aucune ligne de commande. Sélectionnez un fournisseur et cliquez sur "Ajouter ligne" pour commencer.
          </p>
        </div>
      )}
    </div>
  );
};

export default TableauSimulationCommande;