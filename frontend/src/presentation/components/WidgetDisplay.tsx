import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
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

interface WidgetDisplayProps {
  widget: Widget;
  refreshTrigger?: Date;
}

const WidgetDisplay: React.FC<WidgetDisplayProps> = ({ widget, refreshTrigger }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWidgetData();
  }, [widget, refreshTrigger]);

  const fetchWidgetData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let widgetData = null;

      switch (widget.type) {
        case 'stats_card':
          widgetData = await fetchStatsData();
          break;
        case 'bar_chart':
        case 'line_chart':
          widgetData = await fetchChartData();
          break;
        case 'pie_chart':
          widgetData = await fetchPieData();
          break;
        case 'data_table':
          widgetData = await fetchTableData();
          break;
        case 'kpi_metric':
          widgetData = await fetchKPIData();
          break;
        case 'alert_list':
          widgetData = await fetchAlertsData();
          break;
        case 'trend_indicator':
          widgetData = await fetchTrendData();
          break;
        default:
          widgetData = { message: 'Type de widget non supporté' };
      }

      setData(widgetData);
    } catch (err) {
      setError('Erreur lors du chargement des données');
      console.error('Widget data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatsData = async () => {
    const stats = await apiService.getDashboardStats();
    return stats[widget.config.dataSource] || 0;
  };

  const fetchChartData = async () => {
    // Mock data - replace with real API calls based on config
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
        // Could use apiService.getEvolutionStock() here
        return [
          { name: 'S1', value: 120 },
          { name: 'S2', value: 132 },
          { name: 'S3', value: 101 },
          { name: 'S4', value: 134 },
          { name: 'S5', value: 90 },
          { name: 'S6', value: 108 }
        ];
      default:
        return [];
    }
  };

  const fetchPieData = async () => {
    // Mock data - replace with real API calls
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
        return [];
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

  const fetchAlertsData = async () => {
    const alertes = await apiService.getAlertes(false); // Non lues
    return alertes.slice(0, widget.config.maxAlerts || 5);
  };

  const fetchTrendData = async () => {
    // Mock trend data
    return {
      value: 15.3,
      direction: 'up',
      comparison: widget.config.compareWith || 'previous_month'
    };
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
      total_fournisseurs: BuildingOfficeIcon,
      total_articles: CubeIcon,
      total_commandes: DocumentTextIcon,
      alertes_non_lues: ExclamationTriangleIcon,
      articles_stock_bas: TrendingUpIcon,
      commandes_en_cours: ClockIcon
    };
    return icons[dataSource as keyof typeof icons] || ChartBarIcon;
  };

  const formatValue = (value: number, format: string) => {
    switch (format) {
      case 'percentage':
        return `${value}%`;
      case 'currency':
        return `${value.toLocaleString('fr-FR')} €`;
      case 'days':
        return `${value} jours`;
      default:
        return value.toLocaleString('fr-FR');
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center text-red-500">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-8 w-8 mx-auto mb-2" />
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  const renderWidget = () => {
    switch (widget.type) {
      case 'stats_card':
        const IconComponent = getIcon(widget.config.dataSource);
        return (
          <div className="h-full flex items-center">
            <div className="flex items-center w-full">
              <div className={`${getColorClass(widget.config.color)} rounded-md p-3 mr-4`}>
                <IconComponent className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{widget.title}</p>
                <p className="text-2xl font-bold text-gray-900">{data}</p>
              </div>
            </div>
          </div>
        );

      case 'bar_chart':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-4">{widget.title}</h4>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={data}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );

      case 'line_chart':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-4">{widget.title}</h4>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={data}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );

      case 'pie_chart':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-4">{widget.title}</h4>
            <ResponsiveContainer width="100%" height="85%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  dataKey="value"
                >
                  {data?.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        );

      case 'data_table':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-4">{widget.title}</h4>
            <div className="overflow-auto h-5/6">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {data?.slice(0, widget.config.rowCount || 10).map((item: any, index: number) => (
                    <tr key={index}>
                      <td className="px-3 py-2 text-sm text-gray-900 truncate">
                        {item.nom || item.reference || item.numero_commande || `Item ${index + 1}`}
                      </td>
                      <td className="px-3 py-2 text-sm text-gray-500">
                        {item.status || item.stock_actuel || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'kpi_metric':
        return (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <h4 className="text-sm font-medium text-gray-500 mb-4">{widget.title}</h4>
            <div className="text-3xl font-bold text-blue-600">
              {formatValue(data?.value || 0, widget.config.displayFormat)}
            </div>
            {data?.trend && (
              <div className={`text-sm mt-2 flex items-center ${data.trend > 0 ? 'text-green-500' : 'text-red-500'}`}>
                {data.trend > 0 ? (
                  <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                ) : (
                  <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                )}
                {Math.abs(data.trend)}% vs mois dernier
              </div>
            )}
          </div>
        );

      case 'alert_list':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-4">{widget.title}</h4>
            <div className="space-y-2">
              {data?.map((alert: any, index: number) => (
                <div key={alert.id || index} className="flex items-start text-sm">
                  <div className={`w-2 h-2 rounded-full mr-3 mt-1 ${
                    alert.priorite === 'high' || alert.priorite === 'critical' ? 'bg-red-500' :
                    alert.priorite === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-gray-900 truncate">{alert.titre || alert.message}</p>
                    <p className="text-gray-500 text-xs truncate">{alert.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'trend_indicator':
        return (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <h4 className="text-sm font-medium text-gray-500 mb-4">{widget.title}</h4>
            <div className="flex items-center">
              {data?.direction === 'up' ? (
                <ArrowTrendingUpIcon className="h-8 w-8 text-green-500 mr-2" />
              ) : (
                <ArrowTrendingDownIcon className="h-8 w-8 text-red-500 mr-2" />
              )}
              <div>
                <div className="text-xl font-bold text-gray-900">
                  {data?.direction === 'up' ? '+' : ''}{data?.value}%
                </div>
                <div className="text-xs text-gray-500">vs {data?.comparison}</div>
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
            </div>
          </div>
        );
    }
  };

  return <div className="h-full">{renderWidget()}</div>;
};

export default WidgetDisplay;