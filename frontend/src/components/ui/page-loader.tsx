import React from 'react';

export const PageLoader: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary/20 rounded-full"></div>
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin absolute inset-0"></div>
        </div>
        <p className="text-muted-foreground animate-pulse">Cargando...</p>
      </div>
    </div>
  );
};

export const ComponentLoader: React.FC = () => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center space-y-4">
        <div className="relative">
          <div className="w-12 h-12 border-3 border-primary/20 rounded-full"></div>
          <div className="w-12 h-12 border-3 border-primary border-t-transparent rounded-full animate-spin absolute inset-0"></div>
        </div>
      </div>
    </div>
  );
};