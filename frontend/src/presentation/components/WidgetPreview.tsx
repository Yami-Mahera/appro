import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ChartPieIcon, 
  TableCellsIcon, 
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CubeIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, Tooltip } from 'recharts';
import apiService from '../../services/api';

interface Widget {
  id: string;
  type: string;
  title: string;
  config: any;
  position: { x: number; y: number; w: number; h: number };
}

interface WidgetPreviewProps {
  widget: Widget;
}

const WidgetPreview: React.FC<WidgetPreviewProps> = ({ widget }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchWidgetData();
  }, [widget]);

  const fetchWidgetData = async () => {
    try {
      setLoading(true);
      
      let widgetData = null;

      switch (widget.type) {
        case 'kpi_card':
          widgetData = await fetchStatsData();
          break;
        case 'chart_line':
        case 'chart_bar':
          widgetData = await fetchChartData();
          break;
        case 'chart_pie':
          widgetData = await fetchPieData();
          break;
        case 'table':
          widgetData = await fetchTableData();
          break;
        case 'gauge':
          widgetData = await fetchKPIData();
          break;
        default:
          // Données par défaut pour les types non reconnus
          widgetData = getFallbackData();
      }

      setData(widgetData);
    } catch (err) {
      console.warn('Widget preview data fetch error (using fallback data):', err);
      // Au lieu d'afficher une erreur, utiliser des données de fallback
      setData(getFallbackData());
    } finally {
      setLoading(false);
    }
  };

  const fetchStatsData = async () => {
    const stats = await apiService.getDashboardStats();
    const dataKey = widget.config.dataSource || widget.config.kpiType;
    return stats[dataKey] || 0;
  };

  const fetchChartData = async () => {
    // Mock data - identique à WidgetDisplay pour cohérence
    switch (widget.config.dataSource) {
      case 'commandes_par_mois':
        return [
          { name: 'Jan', value: 65 },
          { name: 'Fév', value: 59 },
          { name: 'Mar', value: 80 },
          { name: 'Avr', value: 81 },
          { name: 'Mai', value: 56 },
          { name: 'Jun', value: 55 }
        ];
      case 'evolution_stock':
        return [
          { name: 'S1', value: 120 },
          { name: 'S2', value: 132 },
          { name: 'S3', value: 101 },
          { name: 'S4', value: 134 },
          { name: 'S5', value: 90 },
          { name: 'S6', value: 108 }
        ];
      default:
        return [
          { name: 'Jan', value: 65 },
          { name: 'Fév', value: 59 },
          { name: 'Mar', value: 80 },
          { name: 'Avr', value: 81 },
          { name: 'Mai', value: 56 },
          { name: 'Jun', value: 55 }
        ];
    }
  };

  const fetchPieData = async () => {
    // Mock data - identique à WidgetDisplay
    return [
      { name: 'Électronique', value: 35, color: '#3B82F6' },
      { name: 'Fournitures', value: 25, color: '#10B981' },
      { name: 'Outils', value: 20, color: '#8B5CF6' },
      { name: 'Autres', value: 20, color: '#F59E0B' }
    ];
  };

  const fetchTableData = async () => {
    switch (widget.config.tableType) {
      case 'articles_stock_bas':
        return await apiService.getArticlesStockBas();
      case 'fournisseurs':
        return await apiService.getFournisseurs({ limit: widget.config.rowCount || 10 });
      case 'articles':
        return await apiService.getArticles({ limit: widget.config.rowCount || 10 });
      case 'commandes':
        return await apiService.getCommandes({ limit: widget.config.rowCount || 10 });
      default:
        return getFallbackTableData();
    }
  };

  const fetchKPIData = async () => {
    switch (widget.config.kpiType) {
      case 'taux_service_client':
        return await apiService.getKPIsTauxServiceClient();
      case 'delai_moyen_livraison':
        return await apiService.getKPIsDelaiMoyenLivraison();
      default:
        return { value: 94.5, unit: '%', trend: 2.3 };
    }
  };

  const getFallbackData = () => {
    switch (widget.type) {
      case 'kpi_card':
        // Utiliser des valeurs cohérentes avec WidgetDisplay
        const dataKey = widget.config.kpiType;
        const fallbackStats: Record<string, number> = {
          total_fournisseurs: 45,
          total_articles: 234,
          total_commandes: 156,
          alertes_non_lues: 8,
          articles_stock_bas: 12,
          commandes_en_cours: 0  // Cohérent avec l'API réelle
        };
        return fallbackStats[dataKey] ?? 156;
      case 'chart_line':
      case 'chart_bar':
        return [
          { name: 'Jan', value: 65 },
          { name: 'Fév', value: 59 },
          { name: 'Mar', value: 80 },
          { name: 'Avr', value: 81 },
          { name: 'Mai', value: 56 },
          { name: 'Jun', value: 55 }
        ];
      case 'chart_pie':
        return [
          { name: 'Électronique', value: 35, color: '#3B82F6' },
          { name: 'Fournitures', value: 25, color: '#10B981' },
          { name: 'Outils', value: 20, color: '#8B5CF6' },
          { name: 'Autres', value: 20, color: '#F59E0B' }
        ];
      case 'gauge':
        return { value: 94.5, unit: '%', trend: 2.3 };
      case 'table':
        return getFallbackTableData();
      default:
        return null;
    }
  };

  const getFallbackTableData = () => {
    return [
      { nom: 'Article A', valeur: '150', statut: 'En stock' },
      { nom: 'Article B', valeur: '89', statut: 'Stock bas' },
      { nom: 'Article C', valeur: '67', statut: 'En stock' },
      { nom: 'Article D', valeur: '234', statut: 'En stock' },
      { nom: 'Article E', valeur: '12', statut: 'Rupture' }
    ];
  };
  const getColorClass = (color: string) => {
    const colors = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      purple: 'bg-purple-500',
      red: 'bg-red-500',
      orange: 'bg-orange-500',
      indigo: 'bg-indigo-500'
    };
    return colors[color as keyof typeof colors] || 'bg-blue-500';
  };

  const getIcon = (dataSource: string) => {
    const icons = {
      // Types de données dashboard de base
      total_fournisseurs: BuildingOfficeIcon,
      total_articles: CubeIcon,
      total_commandes: DocumentTextIcon,
      alertes_non_lues: ExclamationTriangleIcon,
      articles_stock_bas: ArrowTrendingUpIcon,
      commandes_en_cours: ClockIcon,
      // Types KPI personnalisés 
      taux_service_client: ChartBarIcon,
      delai_livraison: ClockIcon,
      delai_moyen_livraison: ClockIcon,
      commandes_traitees: DocumentTextIcon,
      rupture_stock: ExclamationTriangleIcon,
      rotation_stock: ArrowTrendingUpIcon,
      performance_fournisseur: BuildingOfficeIcon,
      // Types génériques
      default: ChartBarIcon
    };
    return icons[dataSource as keyof typeof icons] || ChartBarIcon;
  };

  const mockData = {
    // Données de fallback uniquement - les vraies données viennent de l'API
    chartData: [
      { name: 'Jan', value: 65 },
      { name: 'Fév', value: 59 },
      { name: 'Mar', value: 80 },
      { name: 'Avr', value: 81 },
      { name: 'Mai', value: 56 },
      { name: 'Jun', value: 55 }
    ],
    pieData: [
      { name: 'Électronique', value: 35, color: '#3B82F6' },
      { name: 'Fournitures', value: 25, color: '#10B981' },
      { name: 'Outils', value: 20, color: '#8B5CF6' },
      { name: 'Autres', value: 20, color: '#F59E0B' }
    ]
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto mb-2"></div>
          <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">{widget.title}</p>
          <p className="text-xs text-blue-400 dark:text-blue-500">Chargement...</p>
        </div>
      </div>
    );
  }

  const renderWidget = () => {
    switch (widget.type) {
      case 'kpi_card':
        // Utiliser les vraies données de l'API ou fallback
        const displayValue = widget.config.displayFormat === 'percentage' ? `${data || 0}%` : 
                            widget.config.displayFormat === 'currency' ? `€${(data || 0).toLocaleString('fr-FR')}` :
                            widget.config.displayFormat === 'days' ? `${data || 0} jours` : 
                            (data || 0).toLocaleString('fr-FR');
        const target = widget.config.target;
        const IconComponent = getIcon(widget.config.kpiType || 'default');
        return (
          <div className="h-full flex items-center">
            <div className="flex items-center w-full">
              <div className={`${getColorClass(widget.config.color)} rounded-md p-3 mr-4`}>
                <IconComponent className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{widget.title}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{displayValue}</p>
                  {target && (
                    <span className="ml-2 text-xs text-gray-400 dark:text-gray-500">
                      / {target}{widget.config.displayFormat === 'percentage' ? '%' : ''}
                    </span>
                  )}
                </div>
                <div className="text-xs text-green-500 dark:text-green-400 mt-1">↑ +2.3% vs précédent</div>
              </div>
            </div>
          </div>
        );

      case 'chart_line':
        const lineData = data && Array.isArray(data) ? data : mockData.chartData;
        const lineColor = widget.config.chartColor === 'gradient' ? '#8B5CF6' :
                         widget.config.chartColor === 'green' ? '#10B981' :
                         widget.config.chartColor === 'red' ? '#EF4444' :
                         widget.config.chartColor === 'orange' ? '#F59E0B' : '#3B82F6';
        const strokeDasharray = widget.config.lineStyle === 'dashed' ? '5 5' :
                               widget.config.lineStyle === 'dotted' ? '2 2' : '0';
        return (
          <div className="h-full">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">{widget.title}</h4>
              <span className="text-xs text-gray-500 dark:text-gray-400">{widget.config.periode || '6 mois'}</span>
            </div>
            <ResponsiveContainer width="100%" height="80%">
              <LineChart data={lineData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke={lineColor} 
                  strokeWidth={2}
                  strokeDasharray={strokeDasharray}
                  dot={{ fill: lineColor, strokeWidth: 2, r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );

      case 'chart_bar':
        const barData = data && Array.isArray(data) ? data : mockData.chartData;
        const barColor = widget.config.colorScheme === 'green' ? '#10B981' :
                        widget.config.colorScheme === 'multicolor' ? '#8B5CF6' :
                        widget.config.colorScheme === 'gradient' ? '#F59E0B' : '#3B82F6';
        return (
          <div className="h-full">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white">{widget.title}</h4>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {widget.config.orientation === 'horizontal' ? 'Horizontal' : 'Vertical'} - Top {widget.config.maxItems || 10}
              </span>
            </div>
            <ResponsiveContainer width="100%" height="80%">
              <BarChart 
                data={barData.slice(0, widget.config.maxItems || 10)}
              >
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill={barColor} radius={2} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );

      case 'chart_pie':
        const pieData = data && Array.isArray(data) ? data : mockData.pieData;
        const isDonut = widget.config.displayType === 'doughnut';
        const showPercentage = widget.config.showPercentage !== 'false';
        const legendPos = widget.config.legendPosition || 'right';
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-2">{widget.title}</h4>
            <div className="flex h-full">
              <ResponsiveContainer width="70%" height="90%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={isDonut ? 30 : 0}
                    outerRadius={60}
                    dataKey="value"
                    label={showPercentage ? ({ value }: { value?: number }) => 
                      value ? `${value.toFixed(1)}%` : '' : false}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              {legendPos !== 'none' && (
                <div className="flex flex-col justify-center space-y-1 text-xs">
                  {pieData.map((entry, index) => (
                    <div key={index} className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded-sm mr-2" 
                        style={{ backgroundColor: entry.color }}
                      ></div>
                      <span className="truncate">{entry.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        );

      case 'table':
        const tableData = data && Array.isArray(data) && data.length > 0 ? data : getFallbackTableData();
        const rowCount = widget.config.rowCount || 10;
        return (
          <div className="h-full">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-sm font-medium text-gray-900">{widget.title}</h4>
              <span className="text-xs text-gray-500">{rowCount} lignes</span>
            </div>
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                    <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Qté</th>
                    <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {tableData.slice(0, Math.min(rowCount, 5)).map((item: any, index: number) => (
                    <tr key={index}>
                      <td className="px-2 py-1 text-xs text-gray-900 truncate">
                        {item.nom || item.reference || item.numero_commande || `Item ${index + 1}`}
                      </td>
                      <td className="px-2 py-1 text-xs text-gray-900">
                        {item.valeur || item.stock_actuel || item.quantite || 'N/A'}
                      </td>
                      <td className="px-2 py-1 text-xs">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          (item.statut || item.status) === 'En stock' || (item.statut || item.status) === 'en_cours' ? 'bg-green-100 text-green-800' :
                          (item.statut || item.status) === 'Stock bas' || (item.statut || item.status) === 'en_attente' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {item.statut || item.status || 'N/A'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'gauge':
        const gaugeData = data || { value: 78 };
        const currentValue = gaugeData.value || 78;
        const minVal = widget.config.minValue || 0;
        const maxVal = widget.config.maxValue || 100;
        const warningThreshold = widget.config.warningThreshold || 70;
        const criticalThreshold = widget.config.criticalThreshold || 90;
        
        const getGaugeColor = () => {
          if (currentValue >= criticalThreshold) return 'text-red-500';
          if (currentValue >= warningThreshold) return 'text-yellow-500';
          return 'text-green-500';
        };

        const percentage = ((currentValue - minVal) / (maxVal - minVal)) * 100;
        
        return (
          <div className="h-full flex flex-col justify-center items-center">
            <h4 className="text-sm font-medium text-gray-900 mb-4">{widget.title}</h4>
            <div className="relative">
              <svg width="120" height="80" viewBox="0 0 120 80">
                {/* Background arc */}
                <path
                  d="M 20 60 A 40 40 0 0 1 100 60"
                  fill="none"
                  stroke="#E5E7EB"
                  strokeWidth="8"
                  strokeLinecap="round"
                />
                {/* Progress arc */}
                <path
                  d="M 20 60 A 40 40 0 0 1 100 60"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${percentage * 1.26} 126`}
                  className={getGaugeColor()}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center mt-4">
                <span className={`text-xl font-bold ${getGaugeColor()}`}>
                  {currentValue}
                </span>
                <span className="text-xs text-gray-500">
                  {minVal} - {maxVal}
                </span>
              </div>
            </div>
            <div className="flex space-x-4 mt-2 text-xs">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                <span>&lt;{warningThreshold}</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                <span>{warningThreshold}-{criticalThreshold}</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                <span>&gt;{criticalThreshold}</span>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <ChartBarIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <h4 className="text-sm font-medium text-gray-900">{widget.title}</h4>
              <p className="text-xs text-gray-500 mt-1">Type: {widget.type}</p>
              <p className="text-xs text-blue-500 mt-1">Configuration disponible</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="h-full">
      {renderWidget()}
    </div>
  );
};

export default WidgetPreview;