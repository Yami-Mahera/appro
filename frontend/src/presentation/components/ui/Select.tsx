import React, { useState, useRef, useEffect } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

interface SelectTriggerProps {
  children: React.ReactNode;
  onClick?: () => void;
  isOpen?: boolean;
  className?: string;
}

interface SelectValueProps {
  placeholder?: string;
  className?: string;
}

interface SelectContentProps {
  children: React.ReactNode;
  onSelect?: (value: string) => void;
  value?: string;
  className?: string;
}

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
  onSelect?: (value: string) => void;
  isSelected?: boolean;
  className?: string;
}

export const Select: React.FC<SelectProps> = ({ value, onValueChange, children, className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div ref={selectRef} className={`relative ${className}`}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          if (child.type === SelectTrigger) {
            return React.cloneElement(child as React.ReactElement<SelectTriggerProps>, { 
              onClick: () => setIsOpen(!isOpen),
              isOpen 
            });
          }
          if (child.type === SelectContent) {
            return isOpen ? React.cloneElement(child as React.ReactElement<SelectContentProps>, { 
              onSelect: (val: string) => {
                onValueChange(val);
                setIsOpen(false);
              },
              value 
            }) : null;
          }
        }
        return child;
      })}
    </div>
  );
};

export const SelectTrigger: React.FC<SelectTriggerProps> = ({ 
  children, 
  onClick, 
  isOpen, 
  className = '' 
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        w-full px-3 py-2 text-left bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
        focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500
        flex justify-between items-center text-gray-900 dark:text-white
        ${className}
      `}
    >
      {children}
      <ChevronDownIcon 
        className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
      />
    </button>
  );
};

export const SelectValue: React.FC<SelectValueProps> = ({ placeholder, className = '' }) => {
  return (
    <span className={`text-gray-900 dark:text-white ${className}`}>
      {placeholder}
    </span>
  );
};

export const SelectContent: React.FC<SelectContentProps> = ({ 
  children, 
  onSelect, 
  value, 
  className = '' 
}) => {
  return (
    <div className={`
      absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-60 
      overflow-auto ${className}
    `}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child) && child.type === SelectItem) {
          return React.cloneElement(child as React.ReactElement<SelectItemProps>, { 
            onSelect,
            isSelected: (child.props as SelectItemProps).value === value 
          });
        }
        return child;
      })}
    </div>
  );
};

export const SelectItem: React.FC<SelectItemProps> = ({ 
  value, 
  children, 
  onSelect, 
  isSelected, 
  className = '' 
}) => {
  return (
    <div
      onClick={() => onSelect?.(value)}
      className={`
        px-3 py-2 cursor-pointer hover:bg-gray-100 text-sm
        ${isSelected ? 'bg-blue-50 text-blue-600' : 'text-gray-900'}
        ${className}
      `}
    >
      {children}
    </div>
  );
};