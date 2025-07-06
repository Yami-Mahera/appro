import React, { useState, useEffect, createContext, useContext, ReactNode } from 'react';

interface ThemeContextType {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider = ({ children }: ThemeProviderProps) => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Initialize theme on component mount
    const initializeTheme = () => {
      try {
        const savedTheme = localStorage.getItem('theme');
        let shouldBeDark = false;
        
        if (savedTheme) {
          shouldBeDark = savedTheme === 'dark';
        } else {
          // Check system preference
          shouldBeDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
          // Save system preference
          localStorage.setItem('theme', shouldBeDark ? 'dark' : 'light');
        }
        
        setIsDarkMode(shouldBeDark);
        
        // Apply theme immediately to prevent flash
        if (shouldBeDark) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        
        setIsInitialized(true);
      } catch (error) {
        console.warn('Theme initialization failed:', error);
        // Fallback to light mode
        setIsDarkMode(false);
        setIsInitialized(true);
      }
    };

    initializeTheme();
  }, []);

  useEffect(() => {
    // Only apply theme changes after initialization
    if (!isInitialized) return;
    
    try {
      if (isDarkMode) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      }
    } catch (error) {
      console.warn('Theme change failed:', error);
    }
  }, [isDarkMode, isInitialized]);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};