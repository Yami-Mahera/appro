import React, { useState } from 'react';
import { 
  ChartBarIcon, 
  CalculatorIcon, 
  ClipboardDocumentListIcon,
  Squares2X2Icon 
} from '@heroicons/react/24/outline';
import TableauProjectionCouverture from '../components/TableauProjectionCouverture';
import TableauSimulationCommande from '../components/TableauSimulationCommande';
import TableauSuiviCommandes from '../components/TableauSuiviCommandes';

type TabType = 'projection' | 'simulation' | 'suivi';

interface TabConfig {
  key: TabType;
  label: string;
  icon: React.ComponentType<any>;
  description: string;
}

const GestionStocksAvancee: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('projection');

  const tabs: TabConfig[] = [
    {
      key: 'projection',
      label: 'Projection Couverture',
      icon: ChartBarIcon,
      description: 'Tableau de projection de la couverture de stock avec calculs CMS/CMC/QM'
    },
    {
      key: 'simulation',
      label: 'Simulation Commande',
      icon: CalculatorIcon,
      description: 'Simulation avancée de commandes avec validation des contraintes'
    },
    {
      key: 'suivi',
      label: 'Suivi Commandes',
      icon: ClipboardDocumentListIcon,
      description: 'Suivi temps réel des commandes en cours avec alertes'
    }
  ];

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'projection':
        return <TableauProjectionCouverture />;
      case 'simulation':
        return <TableauSimulationCommande />;
      case 'suivi':
        return <TableauSuiviCommandes />;
      default:
        return <TableauProjectionCouverture />;
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm">
        <div className="flex items-center space-x-3 mb-4">
          <Squares2X2Icon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Gestion Avancée des Stocks
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Tableaux sophistiqués pour la projection, simulation et suivi des stocks
            </p>
          </div>
        </div>

        {/* Navigation par onglets */}
        <div className="border-b border-gray-200 dark:border-gray-600">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => {
              const IconComponent = tab.icon;
              const isActive = activeTab === tab.key;
              
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                    isActive
                      ? 'border-blue-500 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
                  }`}
                >
                  <IconComponent 
                    className={`-ml-0.5 mr-2 h-5 w-5 ${
                      isActive ? 'text-blue-500 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'
                    }`} 
                  />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Description de l'onglet actif */}
        <div className="mt-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {tabs.find(tab => tab.key === activeTab)?.description}
          </p>
        </div>
      </div>

      {/* Contenu de l'onglet actif */}
      <div className="min-h-[600px]">
        {renderActiveTab()}
      </div>

      {/* Informations sur les modalités de calcul */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Modalités de Calcul - Rappel des Formules
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">CMS - Couverture Minimale de Sécurité</h4>
            <p className="text-sm text-gray-600 mb-2">
              <strong>Formule:</strong> CMS = VL × (1+Vp) + H × Vp
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <div><strong>VL:</strong> Variation logistique</div>
              <div><strong>Vp:</strong> Variation de la prévision</div>
              <div><strong>H:</strong> Horizon (délai d'acheminement)</div>
              <div><strong>Minimum:</strong> 6 semaines</div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">CMC - Couverture Maximale Commande</h4>
            <p className="text-sm text-gray-600 mb-2">
              <strong>Formule:</strong> CMC = (Dv-10-Da) × (1-Vp) - H × Vp
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <div><strong>Dv:</strong> Durée de vie du produit</div>
              <div><strong>Da:</strong> Délai d'acheminement</div>
              <div><strong>10:</strong> Marge pour consommation optimale</div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-medium text-purple-900 mb-2">QM - Quantité Maximale Commande</h4>
            <p className="text-sm text-gray-600 mb-2">
              <strong>Formule:</strong> QM = CMC - Cr
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <div><strong>Cr:</strong> Couverture réelle avant réception</div>
              <div><strong>Calcul Cr:</strong> Stock / Prévision consommation</div>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Niveaux d'Alerte</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong className="text-blue-900">Nouvelles commandes:</strong>
              <div className="mt-1 space-y-1 text-blue-700">
                <div>• <strong>Normal:</strong> Db - Do - Dc &gt; 4 jours</div>
                <div>• <strong>Urgent:</strong> -4 &lt; Db - Do - Dc &lt; 0</div>
                <div>• <strong>Critique:</strong> Db - Do - Dc &lt; -4</div>
              </div>
            </div>
            <div>
              <strong className="text-blue-900">Commandes en cours:</strong>
              <div className="mt-1 space-y-1 text-blue-700">
                <div>• <strong>Normal:</strong> (Cp-CMS)/(CMS+da) &gt; 10%</div>
                <div>• <strong>À suivre:</strong> 0% &lt; (Cp-CMS)/(CMS+da) &lt; 10%</div>
                <div>• <strong>Urgent:</strong> (Cp-CMS)/(CMS+da) &lt; 0%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GestionStocksAvancee;