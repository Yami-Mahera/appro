import React from 'react';
import { Bars3Icon } from '@heroicons/react/24/outline';
import UserMenu from './UserMenu';
import AlertsMenu from './AlertsMenu';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
      <div className="flex items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
        >
          <Bars3Icon className="h-6 w-6" />
        </button>

        {/* Breadcrumb or page title could go here */}
        <div className="flex-1 md:flex-none">
          {/* This space can be used for breadcrumbs or page titles */}
        </div>

        {/* User menu and alerts */}
        <div className="flex items-center space-x-2">
          <AlertsMenu />
          <UserMenu />
        </div>
      </div>
    </header>
  );
};

export default Header;