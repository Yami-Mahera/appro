import React, { useState, ReactNode } from "react";
import { useAuth } from "../../hooks/useAuth";
import { ThemeProvider } from "../../hooks/useTheme";
import {
  HomeIcon,
  BuildingOfficeIcon,
  CubeIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  UserGroupIcon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";
import { classNames } from "../../common/utils";
import { images } from "../../data/constants/images";
import Header from "./Header";

const navigation = [
  { name: "Dashboard", href: "/", icon: HomeIcon },
  { name: "Fournisseurs", href: "/fournisseurs", icon: BuildingOfficeIcon },
  { name: "Articles", href: "/articles", icon: CubeIcon },
  { name: "Commandes", href: "/commandes", icon: DocumentTextIcon },
  { name: "Reporting", href: "/reporting", icon: ChartBarIcon },
  { name: "Alertes", href: "/alertes", icon: ExclamationTriangleIcon },
  {
    name: "Utilisateurs",
    href: "/users",
    icon: UserGroupIcon,
    adminOnly: true,
  },
];

interface LayoutProps {
  children: ReactNode;
  currentPath?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, currentPath = "/" }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();

  return (
    <ThemeProvider>
      <div className="h-screen flex bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-200">
      {/* Mobile menu */}
      <div
        className={classNames(
          sidebarOpen ? "fixed inset-0 flex z-40 md:hidden" : "hidden"
        )}
      >
        <div
          className="modal-overlay"
          onClick={() => setSidebarOpen(false)}
        ></div>
        <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white shadow-2xl">
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white transition-colors duration-200 hover:bg-white hover:bg-opacity-20"
              onClick={() => setSidebarOpen(false)}
            >
              <XMarkIcon className="h-6 w-6 text-white" />
            </button>
          </div>
          <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto custom-scrollbar">
            <div className="flex-shrink-0 flex items-center px-6 mb-8">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mr-3">
                <HomeIcon className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-800">
                Gestion Approovisionnements
              </h1>
            </div>
            <nav className="px-4 space-y-2">
              {navigation
                .filter(
                  (item) => !item.adminOnly || user?.role === "administrateur"
                )
                .map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className={classNames(
                      "sidebar-link",
                      currentPath === item.href ? "active" : ""
                    )}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </a>
                ))}
            </nav>
          </div>
          {/* User section mobile */}
          <div className="flex-shrink-0 border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center mr-3">
                <span className="text-xs font-medium text-white">
                  {user?.prenom?.[0]}
                  {user?.nom?.[0]}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.prenom} {user?.nom}
                </p>
                <p className="text-xs text-gray-500 truncate">{user?.role}</p>
              </div>
              <button
                onClick={logout}
                className="ml-2 p-1 text-gray-400 hover:text-red-500 transition-colors duration-200"
                title="Se déconnecter"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Static sidebar for desktop */}
      <div className="hidden md:flex md:w-72 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-white shadow-xl border-r border-gray-100">
          <div className="flex-1 flex flex-col pt-8 pb-4 overflow-y-auto custom-scrollbar">
            <div className="flex items-center flex-shrink-0 px-6 mb-10">
              <div className="w-20 h-20 flex items-center justify-center">
                <img src={images.logo} alt="logo star" loading="lazy" />
              </div>
              <div className="flex items-center">
                <h1 className="ml-3 text-lg font-semibold text-gray-900">
                  Gestion des approvisionnements
                </h1>
              </div>
            </div>
            <nav className="flex-1 px-4 space-y-2">
              {navigation
                .filter(
                  (item) => !item.adminOnly || user?.role === "administrateur"
                )
                .map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className={classNames(
                      "sidebar-link",
                      currentPath === item.href ? "active" : ""
                    )}
                  >
                    <item.icon className="mr-4 h-5 w-5" />
                    <span className="font-medium">{item.name}</span>
                  </a>
                ))}
            </nav>
          </div>

          {/* User section desktop */}
          <div className="flex-shrink-0 border-t border-gray-100 p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-xl flex items-center justify-center mr-4 shadow-md">
                <span className="text-sm font-medium text-white">
                  {user?.prenom?.[0]}
                  {user?.nom?.[0]}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user?.prenom} {user?.nom}
                </p>
                <p className="text-xs text-gray-500 truncate capitalize">
                  {user?.role}
                </p>
              </div>
              <button
                onClick={logout}
                className="ml-2 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200"
                title="Se déconnecter"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-72 flex flex-col flex-1 min-h-0">
        {/* Top bar */}
        <div className="sticky top-0 z-30 md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3 bg-white shadow-sm border-b border-gray-200">
          <button
            className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors duration-200"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
        </div>

        {/* Page content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none custom-scrollbar">
          <div className="p-6 lg:p-8">
            <div className="animate-slideIn">{children}</div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
