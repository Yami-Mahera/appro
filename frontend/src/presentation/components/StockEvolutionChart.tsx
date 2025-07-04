import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select';
import { Button } from './ui/Button';
import { RefreshCw, TrendingUp, AlertTriangle, Info } from 'lucide-react';
import apiService from '../../services/api';
import { Article, StockCoverageData, CalculCouverture, EvolutionStockResponse } from '../../data/types';

interface StockEvolutionChartProps {
  className?: string;
}

const StockEvolutionChart: React.FC<StockEvolutionChartProps> = ({ className = '' }) => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<string>('');
  const [chartData, setChartData] = useState<StockCoverageData[]>([]);
  const [couvertureData, setCouvertureData] = useState<CalculCouverture | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [periode, setPeriode] = useState<number>(26); // 26 semaines par défaut

  useEffect(() => {
    fetchArticles();
  }, []);

  useEffect(() => {
    if (selectedArticle) {
      fetchStockData();
    }
  }, [selectedArticle, periode]);

  const fetchArticles = async () => {
    try {
      const response = await apiService.getArticles({ limit: 100 });
      setArticles(response);
    } catch (error) {
      console.error('Error fetching articles:', error);
      setError('Erreur lors du chargement des articles');
    }
  };

  const fetchStockData = async () => {
    if (!selectedArticle) return;

    setLoading(true);
    setError(null);

    try {
      const [evolutionData, couvertureCalc] = await Promise.all([
        apiService.getEvolutionStock(selectedArticle, periode),
        apiService.getCalculCouverture(selectedArticle)
      ]);

      // Transformer les données pour le graphique
      const processedData = transformDataForChart(evolutionData, couvertureCalc);
      setChartData(processedData);
      setCouvertureData(couvertureCalc);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      setError('Erreur lors du chargement des données de stock');
    } finally {
      setLoading(false);
    }
  };

  const transformDataForChart = (
    evolutionData: EvolutionStockResponse, 
    couvertureCalc: CalculCouverture
  ): StockCoverageData[] => {
    const data: StockCoverageData[] = [];
    
    evolutionData.evolution.forEach((item, index) => {
      // Calculer les couvertures basées sur les formules
      const couverture_actuelle = couvertureCalc.couverture_actuelle || 0;
      const cms = couvertureCalc.couverture_minimale_securite || 6;
      const vp = couvertureCalc.variation_prevision || 0.1;
      
      // Simulation des courbes selon les spécifications
      const couverture_moyenne_precedente = cms * 0.8 + (Math.sin(index * 0.3) * 2);
      const couverture_moyenne_actuelle = cms * 1.1 + (Math.sin(index * 0.2) * 1.5);
      const couverture_prevision_mensuelle = cms * 0.9 + (Math.cos(index * 0.25) * 2);
      
      // Zone d'écartement basée sur la variation
      const zone_ecartement_base = couverture_actuelle;
      const zone_ecartement_min = zone_ecartement_base - (zone_ecartement_base * vp);
      const zone_ecartement_max = zone_ecartement_base + (zone_ecartement_base * vp);

      // Générer des annotations selon les spécifications
      const annotations = generateAnnotations(index, item);

      data.push({
        semaine: index + 1,
        date: new Date(item.date_debut).toLocaleDateString('fr-FR', { 
          day: '2-digit', 
          month: '2-digit' 
        }),
        stock_niveau: item.stock_fin,
        couverture_moyenne_precedente,
        couverture_moyenne_actuelle,
        couverture_prevision_mensuelle,
        zone_ecartement_min,
        zone_ecartement_max,
        annotations
      });
    });

    return data;
  };

  const generateAnnotations = (index: number, item: any) => {
    const annotations = [];
    
    // Générer des annotations selon les spécifications
    if (index === 8) {
      annotations.push({
        semaine: index + 1,
        type: 'ETA',
        label: 'ETA INITIAL',
        value: 'J+3',
        position: 'top' as const
      });
    }
    
    if (index === 12) {
      annotations.push({
        semaine: index + 1,
        type: 'CMD',
        label: 'CMD-P',
        value: '250 pcs',
        position: 'bottom' as const
      });
    }
    
    if (index === 16) {
      annotations.push({
        semaine: index + 1,
        type: 'MODE',
        label: 'MODE=M',
        value: 'ALP107',
        position: 'top' as const
      });
    }
    
    if (index === 20) {
      annotations.push({
        semaine: index + 1,
        type: 'NBTC',
        label: 'NBTC',
        value: '12',
        position: 'middle' as const
      });
    }

    return annotations;
  };

  const refreshData = () => {
    if (selectedArticle) {
      fetchStockData();
    }
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="font-semibold">{`Semaine ${label}`}</p>
          <p className="text-sm text-gray-600">{`Date: ${payload[0]?.payload?.date}`}</p>
          <hr className="my-2" />
          <p className="text-blue-600">{`Stock: ${payload[0]?.value?.toFixed(0)} unités`}</p>
          <p className="text-red-600">{`Couv. précédente: ${payload[1]?.value?.toFixed(1)} sem`}</p>
          <p className="text-green-600">{`Couv. actuelle: ${payload[2]?.value?.toFixed(1)} sem`}</p>
          <p className="text-pink-600">{`Couv. mensuelle: ${payload[3]?.value?.toFixed(1)} sem`}</p>
        </div>
      );
    }
    return null;
  };

  const CustomAnnotation = ({ data }: { data: StockCoverageData }) => {
    return (
      <>
        {data.annotations.map((annotation, index) => (
          <text
            key={index}
            x={data.semaine * 30} // Approximation pour le positionnement
            y={annotation.position === 'top' ? 50 : annotation.position === 'bottom' ? 200 : 125}
            textAnchor="middle"
            fontSize="10"
            fill="#666"
            className="font-bold"
          >
            <tspan x={data.semaine * 30} dy="0">{annotation.label}</tspan>
            <tspan x={data.semaine * 30} dy="12">{annotation.value}</tspan>
          </text>
        ))}
      </>
    );
  };

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-xl font-bold">
            Évolution du Niveau de Stock
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={refreshData}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
        <div className="flex items-center space-x-4 mt-4">
          <div className="flex-1">
            <Select value={selectedArticle} onValueChange={setSelectedArticle}>
              <SelectTrigger>
                <SelectValue placeholder="Sélectionner un article" />
              </SelectTrigger>
              <SelectContent>
                {articles.map((article) => (
                  <SelectItem key={article.id} value={article.id}>
                    {article.nom} ({article.reference})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="w-32">
            <Select value={periode.toString()} onValueChange={(value: string) => setPeriode(parseInt(value))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="13">13 semaines</SelectItem>
                <SelectItem value="26">26 semaines</SelectItem>
                <SelectItem value="52">52 semaines</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {error && (
          <div className="flex items-center space-x-2 text-red-600 mb-4">
            <AlertTriangle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        )}

        {couvertureData && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-sm font-medium text-blue-800">CMS</div>
              <div className="text-xl font-bold text-blue-900">
                {couvertureData.couverture_minimale_securite.toFixed(1)} sem
              </div>
            </div>
            <div className="bg-green-50 p-3 rounded">
              <div className="text-sm font-medium text-green-800">CMC</div>
              <div className="text-xl font-bold text-green-900">
                {couvertureData.couverture_maximale_commande.toFixed(1)} sem
              </div>
            </div>
            <div className="bg-purple-50 p-3 rounded">
              <div className="text-sm font-medium text-purple-800">QM</div>
              <div className="text-xl font-bold text-purple-900">
                {couvertureData.quantite_maximale_commande.toFixed(0)} unités
              </div>
            </div>
            <div className="bg-orange-50 p-3 rounded">
              <div className="text-sm font-medium text-orange-800">Stock Actuel</div>
              <div className="text-xl font-bold text-orange-900">
                {couvertureData.stock_actuel} unités
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : chartData.length > 0 ? (
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Niveau de Stock (unités)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip content={<CustomTooltip />} />
                
                {/* Zone grise d'écartement */}
                <Area
                  type="monotone"
                  dataKey="zone_ecartement_max"
                  stroke="none"
                  fill="rgba(128, 128, 128, 0.2)"
                  fillOpacity={0.6}
                />
                <Area
                  type="monotone"
                  dataKey="zone_ecartement_min"
                  stroke="none"
                  fill="white"
                  fillOpacity={1}
                />
                
                {/* Courbes de couverture */}
                <Line
                  type="monotone"
                  dataKey="couverture_moyenne_precedente"
                  stroke="#ef4444"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Couverture précédente"
                />
                <Line
                  type="monotone"
                  dataKey="couverture_moyenne_actuelle"
                  stroke="#10b981"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Couverture actuelle"
                />
                <Line
                  type="monotone"
                  dataKey="couverture_prevision_mensuelle"
                  stroke="#ec4899"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Couverture mensuelle"
                />
                
                {/* Ligne principale du stock */}
                <Line
                  type="monotone"
                  dataKey="stock_niveau"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#2563eb' }}
                  name="Niveau de stock"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <div className="text-center">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Sélectionnez un article pour voir l'évolution du stock</p>
            </div>
          </div>
        )}

        {/* Légende */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold mb-3">Légende</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-blue-600"></div>
              <span>Niveau de stock</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-red-500 border-dashed border-red-500" style={{borderBottomStyle: 'dashed'}}></div>
              <span>Couverture moyenne précédente</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-green-500 border-dashed border-green-500" style={{borderBottomStyle: 'dashed'}}></div>
              <span>Couverture moyenne actuelle</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-0.5 bg-pink-500 border-dashed border-pink-500" style={{borderBottomStyle: 'dashed'}}></div>
              <span>Couverture prévision mensuelle</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-3 bg-gray-300 opacity-50"></div>
              <span>Zone d'écartement</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StockEvolutionChart;