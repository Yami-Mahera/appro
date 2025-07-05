import React, { useState, useEffect } from 'react';
import { 
  XMarkIcon, 
  PencilIcon, 
  PrinterIcon, 
  ShareIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon
} from '@heroicons/react/24/outline';
import WidgetDisplay from './WidgetDisplay';

interface Dashboard {
  id: string;
  nom: string;
  description?: string;
  user_id: string;
  widgets: any[];
  layout: any;
  partage: boolean;
  created_at: string;
  updated_at: string;
}

interface DashboardViewerProps {
  dashboard: Dashboard;
  onClose: () => void;
  onEdit: () => void;
}

const DashboardViewer: React.FC<DashboardViewerProps> = ({
  dashboard,
  onClose,
  onEdit
}) => {
  const [fullscreen, setFullscreen] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<number | null>(null);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  useEffect(() => {
    // Set up auto-refresh if configured
    if (refreshInterval) {
      const interval = setInterval(() => {
        setLastRefresh(new Date());
      }, refreshInterval * 1000);

      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    // Implementation for sharing dashboard
    const shareUrl = `${window.location.origin}/dashboard/shared/${dashboard.id}`;
    navigator.clipboard.writeText(shareUrl).then(() => {
      alert('Lien de partage copié dans le presse-papiers');
    });
  };

  const handleFullscreen = () => {
    if (!fullscreen) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
    setFullscreen(!fullscreen);
  };

  return (
    <div className={`${fullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{dashboard.nom}</h1>
            {dashboard.description && (
              <p className="text-sm text-gray-500 mt-1">{dashboard.description}</p>
            )}
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
              <span>Dernière mise à jour: {lastRefresh.toLocaleTimeString()}</span>
              <span>{dashboard.widgets?.length || 0} widgets</span>
              {dashboard.partage && <span className="text-green-600">Partagé</span>}
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Auto-refresh selector */}
            <select
              value={refreshInterval || ''}
              onChange={(e) => setRefreshInterval(e.target.value ? parseInt(e.target.value) : null)}
              className="text-sm border-gray-300 rounded-md"
            >
              <option value="">Pas de rafraîchissement</option>
              <option value="30">30 secondes</option>
              <option value="60">1 minute</option>
              <option value="300">5 minutes</option>
              <option value="900">15 minutes</option>
            </select>

            <button
              onClick={handleShare}
              className="p-2 text-gray-400 hover:text-blue-600 rounded-lg"
              title="Partager"
            >
              <ShareIcon className="h-5 w-5" />
            </button>

            <button
              onClick={handlePrint}
              className="p-2 text-gray-400 hover:text-blue-600 rounded-lg"
              title="Imprimer"
            >
              <PrinterIcon className="h-5 w-5" />
            </button>

            <button
              onClick={handleFullscreen}
              className="p-2 text-gray-400 hover:text-blue-600 rounded-lg"
              title="Plein écran"
            >
              {fullscreen ? (
                <ArrowsPointingInIcon className="h-5 w-5" />
              ) : (
                <ArrowsPointingOutIcon className="h-5 w-5" />
              )}
            </button>

            <button
              onClick={onEdit}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <PencilIcon className="h-4 w-4 mr-1 inline" />
              Modifier
            </button>

            {!fullscreen && (
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
                title="Fermer"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="p-6 bg-gray-50 min-h-screen">
        {dashboard.widgets && dashboard.widgets.length > 0 ? (
          <div className="grid grid-cols-12 gap-4 auto-rows-max">
            {dashboard.widgets.map((widget) => (
              <div
                key={widget.id}
                className={`col-span-${widget.position?.w || 4} bg-white rounded-lg shadow-sm border border-gray-200 p-4`}
                style={{ 
                  gridColumn: `span ${widget.position?.w || 4}`,
                  minHeight: `${(widget.position?.h || 3) * 80}px`
                }}
              >
                <WidgetDisplay widget={widget} refreshTrigger={lastRefresh} />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900">Tableau de bord vide</h3>
            <p className="text-gray-500 mt-2">
              Ce tableau de bord ne contient aucun widget.
            </p>
            <button
              onClick={onEdit}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PencilIcon className="h-4 w-4 mr-2" />
              Ajouter des widgets
            </button>
          </div>
        )}
      </div>

      {/* Print styles */}
      <style>{`
        @media print {
          .no-print {
            display: none !important;
          }
          body {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }
        }
      `}</style>
    </div>
  );
};

export default DashboardViewer;