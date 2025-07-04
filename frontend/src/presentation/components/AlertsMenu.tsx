import React, { useState, useRef, useEffect } from 'react';
import { BellIcon, ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { classNames } from '../../common/utils';
import apiService from '../../services/api';

interface Alert {
  id: string;
  type: 'stock_bas' | 'commande_retard' | 'fournisseur_inactif' | 'info';
  titre: string;
  message: string;
  lu: boolean;
  created_at: string;
  priority: 'low' | 'medium' | 'high';
}

const AlertsMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen) {
      fetchAlerts();
    }
  }, [isOpen]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/api/alertes?limit=10');
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (alertId: string) => {
    try {
      await apiService.put(`/api/alertes/${alertId}/mark-read`);
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? { ...alert, lu: true } : alert
      ));
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadAlerts = alerts.filter(alert => !alert.lu);
      await Promise.all(
        unreadAlerts.map(alert => apiService.put(`/api/alertes/${alert.id}/mark-read`))
      );
      setAlerts(alerts.map(alert => ({ ...alert, lu: true })));
    } catch (error) {
      console.error('Error marking all alerts as read:', error);
    }
  };

  const unreadCount = alerts.filter(alert => !alert.lu).length;

  const getAlertIcon = (type: string, priority: string) => {
    const iconClass = classNames(
      'h-4 w-4 flex-shrink-0',
      priority === 'high' ? 'text-red-500' : 
      priority === 'medium' ? 'text-yellow-500' : 'text-blue-500'
    );
    
    switch (type) {
      case 'stock_bas':
        return <ExclamationTriangleIcon className={iconClass} />;
      case 'commande_retard':
        return <ExclamationTriangleIcon className={iconClass} />;
      case 'fournisseur_inactif':
        return <ExclamationTriangleIcon className={iconClass} />;
      default:
        return <BellIcon className={iconClass} />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (days > 0) {
      return `${days}j`;
    } else if (hours > 0) {
      return `${hours}h`;
    } else {
      return 'Maintenant';
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 relative"
        title="Alertes"
      >
        <BellIcon className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 rounded-full flex items-center justify-center">
            <span className="text-xs text-white font-medium">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50">
          <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                Alertes
              </h3>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
                >
                  Tout marquer comme lu
                </button>
              )}
            </div>
            {unreadCount > 0 && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {unreadCount} alerte{unreadCount > 1 ? 's' : ''} non lue{unreadCount > 1 ? 's' : ''}
              </p>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="px-4 py-6 text-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  Chargement...
                </p>
              </div>
            ) : alerts.length === 0 ? (
              <div className="px-4 py-6 text-center">
                <CheckCircleIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Aucune alerte
                </p>
              </div>
            ) : (
              <div className="py-1">
                {alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={classNames(
                      'px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors duration-200',
                      !alert.lu ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                    )}
                    onClick={() => markAsRead(alert.id)}
                  >
                    <div className="flex items-start space-x-3">
                      {getAlertIcon(alert.type, alert.priority)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className={classNames(
                            'text-sm font-medium truncate',
                            !alert.lu ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-200'
                          )}>
                            {alert.titre}
                          </p>
                          <span className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0 ml-2">
                            {formatDate(alert.created_at)}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                          {alert.message}
                        </p>
                        {!alert.lu && (
                          <div className="flex items-center mt-2">
                            <div className="h-2 w-2 bg-blue-500 rounded-full mr-2"></div>
                            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                              Non lu
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {alerts.length > 0 && (
            <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-700">
              <button
                onClick={() => {
                  setIsOpen(false);
                  // TODO: Navigate to alerts page
                  window.location.href = '/alertes';
                }}
                className="w-full text-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
              >
                Voir toutes les alertes
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AlertsMenu;