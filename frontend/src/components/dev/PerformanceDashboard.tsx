/**
 * Performance Monitoring Dashboard
 * ===============================
 *
 * Development tool to monitor and analyze application performance
 * in real-time. Shows bundle sizes, render times, memory usage,
 * and provides optimization recommendations.
 */

import React, { useState, useEffect, memo, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  Zap,
  Database,
  Clock,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Info,
  Cpu,
  HardDrive,
  Wifi
} from 'lucide-react';
import { usePerformanceMonitor, globalPerformanceStore } from '@/hooks/usePerformanceMonitor';
import { usePerformanceSettings } from '@/components/providers/OptimizedProviders';
import { VirtualList } from '@/components/ui/virtual-list';

interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  status: 'good' | 'warning' | 'poor';
  threshold: { good: number; warning: number };
}

interface BundleInfo {
  name: string;
  size: number;
  gzipSize?: number;
  loadTime: number;
}

const PerformanceDashboard = memo(() => {
  const [metrics, setMetrics] = useState<Record<string, any>>({});
  const [memoryInfo, setMemoryInfo] = useState<any>(null);
  const [networkInfo, setNetworkInfo] = useState<any>(null);
  const [bundles, setBundles] = useState<BundleInfo[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);

  const { debugPerformance, toggleOptimization, isOptimizationEnabled } = usePerformanceSettings();
  const { getMetrics, logSummary } = usePerformanceMonitor({
    componentName: 'PerformanceDashboard'
  });

  // Core performance metrics
  const coreMetrics = useMemo((): PerformanceMetric[] => [
    {
      name: 'First Contentful Paint',
      value: getNavigationTiming('first-contentful-paint') || 0,
      unit: 'ms',
      status: getNavigationTiming('first-contentful-paint') < 1500 ? 'good' :
              getNavigationTiming('first-contentful-paint') < 2500 ? 'warning' : 'poor',
      threshold: { good: 1500, warning: 2500 }
    },
    {
      name: 'Largest Contentful Paint',
      value: getLCPValue() || 0,
      unit: 'ms',
      status: getLCPValue() < 2500 ? 'good' :
              getLCPValue() < 4000 ? 'warning' : 'poor',
      threshold: { good: 2500, warning: 4000 }
    },
    {
      name: 'Time to Interactive',
      value: getNavigationTiming('interactive') || 0,
      unit: 'ms',
      status: getNavigationTiming('interactive') < 3800 ? 'good' :
              getNavigationTiming('interactive') < 7300 ? 'warning' : 'poor',
      threshold: { good: 3800, warning: 7300 }
    },
    {
      name: 'Bundle Size (JS)',
      value: getBundleSize(),
      unit: 'KB',
      status: getBundleSize() < 250 ? 'good' :
              getBundleSize() < 500 ? 'warning' : 'poor',
      threshold: { good: 250, warning: 500 }
    }
  ], []);

  // Update metrics periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(globalPerformanceStore.getAllMetrics());
      updateMemoryInfo();
      updateNetworkInfo();
      updateBundleInfo();
      generateRecommendations();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  function getNavigationTiming(metric: string): number {
    if (typeof window === 'undefined' || !window.performance) return 0;

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (!navigation) return 0;

    switch (metric) {
      case 'first-contentful-paint':
        const fcp = performance.getEntriesByName('first-contentful-paint')[0];
        return fcp ? fcp.startTime : 0;
      case 'interactive':
        return navigation.domInteractive - navigation.navigationStart;
      default:
        return 0;
    }
  }

  function getLCPValue(): number {
    if (typeof window === 'undefined') return 0;

    const lcp = performance.getEntriesByType('largest-contentful-paint').pop();
    return lcp ? lcp.startTime : 0;
  }

  function getBundleSize(): number {
    if (typeof window === 'undefined') return 0;

    const resources = performance.getEntriesByType('resource');
    const jsResources = resources.filter(r => r.name.includes('.js') && r.name.includes('assets'));

    return jsResources.reduce((total, resource) => {
      return total + ((resource as any).transferSize || 0);
    }, 0) / 1024; // Convert to KB
  }

  function updateMemoryInfo() {
    if ('memory' in performance && (performance as any).memory) {
      const memory = (performance as any).memory;
      setMemoryInfo({
        used: Math.round(memory.usedJSHeapSize / 1024 / 1024),
        total: Math.round(memory.totalJSHeapSize / 1024 / 1024),
        limit: Math.round(memory.jsHeapSizeLimit / 1024 / 1024),
        percentage: Math.round((memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100)
      });
    }
  }

  function updateNetworkInfo() {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      setNetworkInfo({
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData
      });
    }
  }

  function updateBundleInfo() {
    if (typeof window === 'undefined') return;

    const resources = performance.getEntriesByType('resource');
    const jsResources = resources.filter(r =>
      r.name.includes('.js') && r.name.includes('assets')
    );

    const bundleData: BundleInfo[] = jsResources.map(resource => ({
      name: resource.name.split('/').pop() || 'unknown',
      size: Math.round(((resource as any).transferSize || 0) / 1024),
      loadTime: Math.round(resource.responseEnd - resource.requestStart)
    }));

    setBundles(bundleData);
  }

  function generateRecommendations() {
    const recs: string[] = [];

    if (getBundleSize() > 500) {
      recs.push('Consider code splitting to reduce bundle size');
    }

    if (getNavigationTiming('first-contentful-paint') > 2500) {
      recs.push('Optimize critical rendering path for faster FCP');
    }

    if (memoryInfo && memoryInfo.percentage > 80) {
      recs.push('High memory usage detected - check for memory leaks');
    }

    if (Object.keys(metrics).length > 10) {
      const worstPerformers = globalPerformanceStore.getWorstPerformers(3);
      if (worstPerformers.length > 0) {
        recs.push(`Optimize slow components: ${worstPerformers.map(p => p.name).join(', ')}`);
      }
    }

    setRecommendations(recs);
  }

  function getStatusColor(status: 'good' | 'warning' | 'poor'): string {
    switch (status) {
      case 'good': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'poor': return 'text-red-500';
      default: return 'text-gray-500';
    }
  }

  function getStatusIcon(status: 'good' | 'warning' | 'poor') {
    switch (status) {
      case 'good': return <CheckCircle className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'poor': return <TrendingDown className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  }

  if (!debugPerformance && process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Card className="w-96 max-h-96 overflow-hidden shadow-xl border-2">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Performance Monitor
            </CardTitle>
            <div className="flex gap-1">
              <Button
                size="sm"
                variant="outline"
                onClick={toggleOptimization}
                className="h-6 text-xs"
              >
                {isOptimizationEnabled ? 'Disable' : 'Enable'}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={logSummary}
                className="h-6 text-xs"
              >
                Log
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-4 pt-0">
          <Tabs defaultValue="metrics" className="w-full">
            <TabsList className="grid w-full grid-cols-4 text-xs">
              <TabsTrigger value="metrics" className="text-xs">Metrics</TabsTrigger>
              <TabsTrigger value="bundles" className="text-xs">Bundles</TabsTrigger>
              <TabsTrigger value="memory" className="text-xs">Memory</TabsTrigger>
              <TabsTrigger value="tips" className="text-xs">Tips</TabsTrigger>
            </TabsList>

            <TabsContent value="metrics" className="space-y-2">
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {coreMetrics.map((metric, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
                    <div className="flex items-center gap-2">
                      <span className={getStatusColor(metric.status)}>
                        {getStatusIcon(metric.status)}
                      </span>
                      <span className="font-medium">{metric.name}</span>
                    </div>
                    <Badge variant={metric.status === 'good' ? 'default' : 'destructive'}>
                      {metric.value.toFixed(0)}{metric.unit}
                    </Badge>
                  </div>
                ))}

                {Object.entries(metrics).map(([name, data]) => (
                  <div key={name} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
                    <span className="font-medium truncate">{name}</span>
                    <Badge variant="outline">
                      {data.averageRenderTime?.toFixed(1)}ms
                    </Badge>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="bundles" className="space-y-2">
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {bundles.map((bundle, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
                    <div className="flex items-center gap-2">
                      <Zap className="w-3 h-3" />
                      <span className="font-medium truncate" title={bundle.name}>
                        {bundle.name.substring(0, 20)}...
                      </span>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline">{bundle.size}KB</Badge>
                      <div className="text-xs text-gray-500">{bundle.loadTime}ms</div>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="memory" className="space-y-3">
              {memoryInfo && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4" />
                      Memory Usage
                    </div>
                    <span>{memoryInfo.percentage}%</span>
                  </div>
                  <Progress value={memoryInfo.percentage} className="h-2" />
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-medium">Used</div>
                      <div>{memoryInfo.used}MB</div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-medium">Limit</div>
                      <div>{memoryInfo.limit}MB</div>
                    </div>
                  </div>
                </div>
              )}

              {networkInfo && (
                <div className="space-y-2 border-t pt-3">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Wifi className="w-4 h-4" />
                    Network
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-medium">Type</div>
                      <div>{networkInfo.effectiveType}</div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-medium">Speed</div>
                      <div>{networkInfo.downlink} Mbps</div>
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="tips" className="space-y-2">
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {recommendations.length > 0 ? (
                  recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start gap-2 p-2 bg-yellow-50 rounded text-xs">
                      <TrendingUp className="w-3 h-3 text-yellow-600 mt-0.5 flex-shrink-0" />
                      <span className="text-yellow-800">{rec}</span>
                    </div>
                  ))
                ) : (
                  <div className="flex items-center gap-2 p-2 bg-green-50 rounded text-xs">
                    <CheckCircle className="w-3 h-3 text-green-600" />
                    <span className="text-green-800">Performance looks good!</span>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
});

PerformanceDashboard.displayName = 'PerformanceDashboard';

export default PerformanceDashboard;
