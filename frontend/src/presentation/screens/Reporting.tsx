import React, { useState, useEffect } from 'react';
import { 
  DocumentArrowDownIcon,
  PrinterIcon,
  TableCellsIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';
import ApiService from '../../services/api';

interface ReportData {
  fournisseurs?: any[];
  articles?: any[];
  commandes?: any[];
  synthese?: any;
}

type ReportType = 'fournisseurs' | 'articles' | 'commandes' | 'synthese';

const Reporting: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeReport, setActiveReport] = useState<ReportType>('synthese');
  const [reportData, setReportData] = useState<ReportData>({});
  const [dateRange, setDateRange] = useState({
    date_from: '',
    date_to: ''
  });

  useEffect(() => {
    loadReport();
  }, [activeReport, dateRange]);

  const loadReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔍 Loading report for:', activeReport);
      
      const params = {
        date_from: dateRange.date_from || undefined,
        date_to: dateRange.date_to || undefined
      };

      console.log('📅 Params:', params);

      let data;
      switch (activeReport) {
        case 'fournisseurs':
          console.log('📊 Calling getFournisseursReport...');
          data = await ApiService.getFournisseursReport(params);
          console.log('✅ Fournisseurs data:', data);
          setReportData({ fournisseurs: data });
          break;
        case 'articles':
          console.log('📊 Calling getArticlesReport...');
          data = await ApiService.getArticlesReport(params);
          console.log('✅ Articles data:', data);
          setReportData({ articles: data });
          break;
        case 'commandes':
          console.log('📊 Calling getCommandesReport...');
          data = await ApiService.getCommandesReport(params);
          console.log('✅ Commandes data:', data);
          setReportData({ commandes: data });
          break;
        case 'synthese':
          console.log('📊 Calling getSyntheseReport...');
          data = await ApiService.getSyntheseReport(params);
          console.log('✅ Synthese data:', data);
          setReportData({ synthese: data });
          break;
      }
      console.log('🎉 Report loaded successfully!');
    } catch (err: any) {
      console.error('❌ Error loading report:', err);
      console.error('❌ Error response:', err.response);
      setError(err.response?.data?.detail || err.message || 'Erreur lors du chargement du rapport');
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = () => {
    // Pour l'instant, on utilise window.print() qui permet d'exporter en PDF
    window.print();
  };

  const exportToExcel = () => {
    // Export CSV simple
    let csvContent = '';
    let headers: string[] = [];
    let rows: (string | number)[][] = [];

    switch (activeReport) {
      case 'fournisseurs':
        headers = ['Nom', 'Code', 'Ville', 'Pays', 'Email', 'Téléphone', 'Total Articles', 'Total Commandes', 'Valeur Stock'];
        rows = reportData.fournisseurs?.map(f => [
          f.nom, f.code_fournisseur, f.ville, f.pays, f.email || '', f.telephone || '',
          f.total_articles, f.total_commandes, f.valeur_stock?.toFixed(2) || '0'
        ]) || [];
        break;
      case 'articles':
        headers = ['Référence', 'Nom', 'Famille', 'Fournisseur', 'Prix Unitaire', 'Stock Actuel', 'Seuil Min', 'Valeur Stock', 'Statut'];
        rows = reportData.articles?.map(a => [
          a.reference, a.nom, a.famille || '', a.fournisseur_nom || '', a.prix_unitaire?.toFixed(2) || '0',
          a.stock_actuel, a.seuil_min, a.valeur_stock?.toFixed(2) || '0', a.stock_status
        ]) || [];
        break;
      case 'commandes':
        headers = ['N° Commande', 'Fournisseur', 'Statut', 'Total HT', 'Total TTC', 'Date Commande', 'Livraison Prévue', 'Créé par'];
        rows = reportData.commandes?.map(c => [
          c.numero_commande, c.fournisseur_nom || '', c.status, c.total_ht?.toFixed(2) || '0',
          c.total_ttc?.toFixed(2) || '0', c.date_commande || '', c.date_livraison_prevue || '', c.created_by_name || ''
        ]) || [];
        break;
    }

    if (headers.length > 0) {
      csvContent = headers.join(',') + '\n';
      rows.forEach(row => {
        csvContent += row.map((cell: string | number) => `"${cell}"`).join(',') + '\n';
      });

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `rapport_${activeReport}_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
  };

  const printReport = () => {
    window.print();
  };

  const resetDateRange = () => {
    setDateRange({ date_from: '', date_to: '' });
  };

  const REPORT_TYPES = [
    { key: 'synthese', label: 'Synthèse', icon: ChartBarIcon },
    { key: 'fournisseurs', label: 'Fournisseurs', icon: TableCellsIcon },
    { key: 'articles', label: 'Articles', icon: TableCellsIcon },
    { key: 'commandes', label: 'Commandes', icon: TableCellsIcon }
  ];

  return (
    <div className="space-y-6 print:space-y-4">
      {/* Header - Hide on print */}
      <div className="print:hidden">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Rapports</h1>
          <div className="flex space-x-2">
            <button
              onClick={exportToPDF}
              className="bg-red-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-red-700"
            >
              <DocumentArrowDownIcon className="w-5 h-5" />
              <span>PDF</span>
            </button>
            <button
              onClick={exportToExcel}
              className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-green-700"
            >
              <TableCellsIcon className="w-5 h-5" />
              <span>Excel</span>
            </button>
            <button
              onClick={printReport}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-gray-700"
            >
              <PrinterIcon className="w-5 h-5" />
              <span>Imprimer</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Report Type Selection */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
          <div className="flex flex-wrap gap-2 mb-4">
            {REPORT_TYPES.map((type) => {
              const IconComponent = type.icon;
              return (
                <button
                  key={type.key}
                  onClick={() => setActiveReport(type.key as ReportType)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                    activeReport === type.key
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <IconComponent className="w-5 h-5" />
                  <span>{type.label}</span>
                </button>
              );
            })}
          </div>

          {/* Date Range Filter */}
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <CalendarDaysIcon className="w-5 h-5 text-gray-400 dark:text-gray-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Période:</span>
            </div>
            <div className="flex space-x-2">
              <input
                type="date"
                value={dateRange.date_from}
                onChange={(e) => setDateRange({ ...dateRange, date_from: e.target.value })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="text-gray-500 dark:text-gray-400 self-center">à</span>
              <input
                type="date"
                value={dateRange.date_to}
                onChange={(e) => setDateRange({ ...dateRange, date_to: e.target.value })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            {(dateRange.date_from || dateRange.date_to) && (
              <button
                onClick={resetDateRange}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm"
              >
                Réinitialiser
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Print Header - Show only on print */}
      <div className="hidden print:block text-center border-b pb-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Rapport {REPORT_TYPES.find(t => t.key === activeReport)?.label}</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Généré le {new Date().toLocaleDateString('fr-FR')} à {new Date().toLocaleTimeString('fr-FR')}
        </p>
        {(dateRange.date_from || dateRange.date_to) && (
          <p className="text-gray-600 dark:text-gray-400">
            Période: {dateRange.date_from ? new Date(dateRange.date_from).toLocaleDateString('fr-FR') : '...'} - {dateRange.date_to ? new Date(dateRange.date_to).toLocaleDateString('fr-FR') : '...'}
          </p>
        )}
      </div>

      {loading && (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {!loading && (
        <>
          {/* Synthese Report */}
          {activeReport === 'synthese' && reportData.synthese && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold mb-6 text-gray-900 dark:text-white">Rapport de synthèse</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">Fournisseurs</h3>
                  <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{reportData.synthese.total_fournisseurs}</p>
                  <p className="text-sm text-blue-700 dark:text-blue-300">Total actifs</p>
                </div>
                
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-2">Articles</h3>
                  <p className="text-3xl font-bold text-green-600 dark:text-green-400">{reportData.synthese.total_articles}</p>
                  <p className="text-sm text-green-700 dark:text-green-300">Total en stock</p>
                </div>
                
                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-2">Commandes</h3>
                  <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">{reportData.synthese.total_commandes}</p>
                  <p className="text-sm text-purple-700 dark:text-purple-300">Total créées</p>
                </div>
                
                <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-2">Stock bas</h3>
                  <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{reportData.synthese.articles_stock_bas}</p>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">Articles en alerte</p>
                </div>
                
                <div className="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-indigo-900 dark:text-indigo-100 mb-2">Valeur stock</h3>
                  <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">{reportData.synthese.valeur_totale_stock?.toFixed(2) || '0'}€</p>
                  <p className="text-sm text-indigo-700 dark:text-indigo-300">Total inventaire</p>
                </div>
                
                <div className="bg-pink-50 dark:bg-pink-900/20 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-pink-900 dark:text-pink-100 mb-2">CA Commandes</h3>
                  <p className="text-3xl font-bold text-pink-600 dark:text-pink-400">{reportData.synthese.valeur_totale_commandes?.toFixed(2) || '0'}€</p>
                  <p className="text-sm text-pink-700 dark:text-pink-300">Chiffre d'affaires</p>
                </div>
              </div>

              {/* Commandes par statut */}
              {reportData.synthese.commandes_par_statut && reportData.synthese.commandes_par_statut.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Répartition des commandes par statut</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {reportData.synthese.commandes_par_statut.map((item: any, index: number) => (
                      <div key={index} className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                        <p className="font-medium capitalize text-gray-900 dark:text-white">{item._id}</p>
                        <p className="text-2xl font-bold text-gray-700 dark:text-gray-200">{item.count}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Fournisseurs Report */}
          {activeReport === 'fournisseurs' && reportData.fournisseurs && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Rapport des fournisseurs</h2>
                <p className="text-gray-600 dark:text-gray-400">{reportData.fournisseurs.length} fournisseur(s) trouvé(s)</p>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Nom</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Code</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Localisation</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Contact</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Articles</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Commandes</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Valeur Stock</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {reportData.fournisseurs.map((fournisseur: any, index: number) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                          {fournisseur.nom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {fournisseur.code_fournisseur}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {fournisseur.ville}, {fournisseur.pays}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          <div>
                            {fournisseur.email && <div>{fournisseur.email}</div>}
                            {fournisseur.telephone && <div>{fournisseur.telephone}</div>}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {fournisseur.total_articles || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {fournisseur.total_commandes || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {fournisseur.valeur_stock?.toFixed(2) || '0.00'}€
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Articles Report */}
          {activeReport === 'articles' && reportData.articles && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Rapport des articles</h2>
                <p className="text-gray-600 dark:text-gray-400">{reportData.articles.length} article(s) trouvé(s)</p>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Référence</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Famille</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fournisseur</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valeur</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {reportData.articles.map((article: any, index: number) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {article.reference}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {article.nom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {article.famille || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {article.fournisseur_nom || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {article.prix_unitaire?.toFixed(2) || '0.00'}€
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {article.stock_actuel} / {article.seuil_min} min
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {article.valeur_stock?.toFixed(2) || '0.00'}€
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            article.stock_status === 'Critique' ? 'bg-red-100 text-red-800' :
                            article.stock_status === 'Bas' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {article.stock_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Commandes Report */}
          {activeReport === 'commandes' && reportData.commandes && (
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <div className="p-6 border-b">
                <h2 className="text-xl font-bold">Rapport des commandes</h2>
                <p className="text-gray-600">{reportData.commandes.length} commande(s) trouvée(s)</p>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">N° Commande</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fournisseur</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total HT</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total TTC</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date Commande</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Livraison Prévue</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Créé par</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {reportData.commandes.map((commande: any, index: number) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {commande.numero_commande}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {commande.fournisseur_nom || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                            {commande.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {commande.total_ht?.toFixed(2) || '0.00'}€
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {commande.total_ttc?.toFixed(2) || '0.00'}€
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {commande.date_commande ? new Date(commande.date_commande).toLocaleDateString('fr-FR') : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {commande.date_livraison_prevue ? new Date(commande.date_livraison_prevue).toLocaleDateString('fr-FR') : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {commande.created_by_name || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Reporting;