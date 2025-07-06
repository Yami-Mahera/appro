import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../hooks/useTheme';
import {
  SunIcon,
  MoonIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import { classNames } from '../../common/utils';

const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
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

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  const menuItems = [
    {
      name: 'Profil',
      icon: UserIcon,
      action: () => {
        // TODO: Navigate to profile page
        console.log('Navigate to profile');
        setIsOpen(false);
      },
    },
    {
      name: 'Paramètres',
      icon: Cog6ToothIcon,
      action: () => {
        // TODO: Navigate to settings page
        console.log('Navigate to settings');
        setIsOpen(false);
      },
    },
    {
      name: 'Déconnexion',
      icon: ArrowRightOnRectangleIcon,
      action: handleLogout,
      isDanger: true,
    },
  ];

  return (
    <div className="flex items-center space-x-4">
      {/* Dark Mode Toggle */}
      <button
        onClick={toggleDarkMode}
        className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
        title={isDarkMode ? 'Mode clair' : 'Mode sombre'}
      >
        {isDarkMode ? (
          <SunIcon className="h-5 w-5" />
        ) : (
          <MoonIcon className="h-5 w-5" />
        )}
      </button>

      {/* User Menu */}
      <div className="relative" ref={menuRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-3 p-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-md">
            <span className="text-xs font-medium text-white">
              {user?.prenom?.[0]}{user?.nom?.[0]}
            </span>
          </div>
          <div className="hidden md:block text-left">
            <p className="text-sm font-medium">
              {user?.prenom} {user?.nom}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">
              {user?.role}
            </p>
          </div>
          <ChevronDownIcon className={classNames(
            'h-4 w-4 transition-transform duration-200',
            isOpen ? 'rotate-180' : ''
          )} />
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50">
            <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user?.prenom} {user?.nom}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {user?.email}
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 capitalize font-medium">
                {user?.role}
              </p>
            </div>
            <div className="py-1">
              {menuItems.map((item) => (
                <button
                  key={item.name}
                  onClick={item.action}
                  className={classNames(
                    'w-full flex items-center px-4 py-2 text-sm transition-colors duration-200',
                    item.isDanger
                      ? 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  )}
                >
                  <item.icon className="h-4 w-4 mr-3" />
                  {item.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserMenu;