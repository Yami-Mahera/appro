import React from 'react';
import { 
  ChartBarIcon, 
  ChartPieIcon, 
  TableCellsIcon, 
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CubeIcon,
  BuildingOfficeIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

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

  const mockData = {
    stats: {
      total_fournisseurs: 45,
      total_articles: 234,
      total_commandes: 156,
      alertes_non_lues: 8,
      articles_stock_bas: 12,
      commandes_en_cours: 23
    },
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
    ],
    alerts: [
      { id: 1, message: 'Stock bas: Vis M6', priority: 'high' },
      { id: 2, message: 'Retard livraison CMD-001', priority: 'medium' },
      { id: 3, message: 'Nouveau fournisseur', priority: 'low' }
    ]
  };

  const renderWidget = () => {
    switch (widget.type) {
      case 'stats_card':
        const statValue = mockData.stats[widget.config.dataSource as keyof typeof mockData.stats] || 0;
        const IconComponent = getIcon(widget.config.dataSource);
        return (
          <div className="h-full flex items-center">
            <div className="flex items-center w-full">
              <div className={`${getColorClass(widget.config.color)} rounded-md p-3 mr-4`}>
                <IconComponent className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">{widget.title}</p>
                <p className="text-2xl font-bold text-gray-900">{statValue}</p>
              </div>
            </div>
          </div>
        );

      case 'bar_chart':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-2">{widget.title}</h4>
            <ResponsiveContainer width="100%" height="80%">
              <BarChart data={mockData.chartData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );

      case 'line_chart':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-2">{widget.title}</h4>
            <ResponsiveContainer width="100%" height="80%">
              <LineChart data={mockData.chartData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );

      case 'pie_chart':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-2">{widget.title}</h4>
            <ResponsiveContainer width="100%" height="80%">
              <PieChart>
                <Pie
                  data={mockData.pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={60}
                  dataKey="value"
                >
                  {mockData.pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        );

      case 'data_table':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-2">{widget.title}</h4>
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                    <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Valeur</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  <tr><td className="px-2 py-1 text-xs">Article A</td><td className="px-2 py-1 text-xs">150</td></tr>
                  <tr><td className="px-2 py-1 text-xs">Article B</td><td className="px-2 py-1 text-xs">89</td></tr>
                  <tr><td className="px-2 py-1 text-xs">Article C</td><td className="px-2 py-1 text-xs">67</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'kpi_metric':
        return (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <h4 className="text-sm font-medium text-gray-500 mb-2">{widget.title}</h4>
            <div className="text-3xl font-bold text-blue-600">94.5%</div>
            <div className="text-xs text-green-500 mt-1">↑ +2.3% vs mois dernier</div>
          </div>
        );

      case 'alert_list':
        return (
          <div className="h-full">
            <h4 className="text-sm font-medium text-gray-900 mb-2">{widget.title}</h4>
            <div className="space-y-2">
              {mockData.alerts.slice(0, widget.config.maxAlerts || 5).map((alert) => (
                <div key={alert.id} className="flex items-center text-xs">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    alert.priority === 'high' ? 'bg-red-500' :
                    alert.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <span className="truncate">{alert.message}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'trend_indicator':
        return (
          <div className="h-full flex flex-col justify-center items-center text-center">
            <h4 className="text-sm font-medium text-gray-500 mb-2">{widget.title}</h4>
            <div className="flex items-center">
              <TrendingUpIcon className="h-8 w-8 text-green-500 mr-2" />
              <div>
                <div className="text-xl font-bold text-gray-900">+15.3%</div>
                <div className="text-xs text-gray-500">vs {widget.config.compareWith || 'mois précédent'}</div>
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

  return (
    <div className="h-full">
      {renderWidget()}
    </div>
  );
};

export default WidgetPreview;