import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { lazyWithPreload, lazyWithNamedExport } from '../lazyWithPreload';

// Mock React.lazy
const mockLazy = jest.spyOn(React, 'lazy');

describe('lazyWithPreload', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('lazyWithPreload', () => {
    it('creates lazy component with preload capability', () => {
      const mockImport = jest.fn(() => Promise.resolve({ default: () => <div>Test</div> }));

      const LazyComponent = lazyWithPreload(mockImport);

      expect(mockLazy).toHaveBeenCalledWith(mockImport);
      expect(typeof LazyComponent.preload).toBe('function');
    });

    it('preloads component when preload is called', async () => {
      const mockImport = jest.fn(() => Promise.resolve({ default: () => <div>Preloaded</div> }));

      const LazyComponent = lazyWithPreload(mockImport);

      await LazyComponent.preload();

      expect(mockImport).toHaveBeenCalled();
    });

    it('caches preload results', async () => {
      const mockImport = jest.fn(() => Promise.resolve({ default: () => <div>Cached</div> }));

      const LazyComponent = lazyWithPreload(mockImport);

      await LazyComponent.preload();
      await LazyComponent.preload();

      expect(mockImport).toHaveBeenCalledTimes(1);
    });
  });

  describe('lazyWithNamedExport', () => {
    it('creates lazy component for named exports', () => {
      const mockImport = jest.fn(() => Promise.resolve({
        NamedComponent: () => <div>Named Export</div>
      }));

      const LazyComponent = lazyWithNamedExport(mockImport, 'NamedComponent');

      expect(mockLazy).toHaveBeenCalled();
      expect(typeof LazyComponent.preload).toBe('function');
    });

    it('properly extracts named export', async () => {
      const NamedComponent = () => <div>Named Export Test</div>;
      const mockImport = jest.fn(() => Promise.resolve({ NamedComponent }));

      const LazyComponent = lazyWithNamedExport(mockImport, 'NamedComponent');

      await LazyComponent.preload();

      expect(mockImport).toHaveBeenCalled();
    });

    it('handles missing named exports', async () => {
      const mockImport = jest.fn(() => Promise.resolve({ OtherComponent: () => <div>Other</div> }));

      const LazyComponent = lazyWithNamedExport(mockImport, 'MissingComponent');

      await expect(LazyComponent.preload()).rejects.toThrow();
    });
  });

  describe('integration with React.Suspense', () => {
    it('works with Suspense boundary', async () => {
      const TestComponent = () => <div>Lazy Loaded</div>;
      const mockImport = jest.fn(() => Promise.resolve({ default: TestComponent }));

      const LazyComponent = lazyWithPreload(mockImport);

      const { getByText } = render(
        <React.Suspense fallback={<div>Loading...</div>}>
          <LazyComponent />
        </React.Suspense>
      );

      expect(getByText('Loading...')).toBeInTheDocument();

      await waitFor(() => {
        expect(getByText('Lazy Loaded')).toBeInTheDocument();
      });
    });
  });
});
