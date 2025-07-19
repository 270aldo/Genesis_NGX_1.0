
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PredictiveAlerts } from '../wearables/PredictiveAlerts';
import { BiometricsHeader } from './BiometricsHeader';
import { BiometricsMetrics } from './BiometricsMetrics';
import { BiometricsCharts } from './BiometricsCharts';

export const BiometricsOverview: React.FC = () => {
  return (
    <div className="space-y-6">
      <BiometricsHeader />
      
      <BiometricsMetrics />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <BiometricsCharts />

        {/* Right Column - Predictive Alerts */}
        <div className="space-y-6">
          <Card className="bg-white/5 backdrop-blur-xl border border-purple-500/20">
            <CardHeader>
              <CardTitle className="text-white/80">AI Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <PredictiveAlerts />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
