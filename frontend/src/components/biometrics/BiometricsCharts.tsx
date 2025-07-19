
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, AreaChart, Area } from 'recharts';

// Mock biometric data enhanced with wearable integration
const mockData = [
  { date: '2024-01-01', hrv: 45, rhr: 58, sleep: 7.2, energy: 78 },
  { date: '2024-01-02', hrv: 48, rhr: 56, sleep: 8.1, energy: 82 },
  { date: '2024-01-03', hrv: 42, rhr: 61, sleep: 6.8, energy: 71 },
  { date: '2024-01-04', hrv: 51, rhr: 55, sleep: 7.9, energy: 85 },
  { date: '2024-01-05', hrv: 46, rhr: 59, sleep: 7.5, energy: 79 },
  { date: '2024-01-06', hrv: 49, rhr: 57, sleep: 8.3, energy: 88 },
  { date: '2024-01-07', hrv: 53, rhr: 54, sleep: 8.0, energy: 90 },
];

export const BiometricsCharts: React.FC = () => {
  return (
    <div className="lg:col-span-2 space-y-6">
      {/* HRV Trend */}
      <Card className="bg-white/5 backdrop-blur-xl border border-purple-500/20">
        <CardHeader>
          <CardTitle className="text-white/80">Heart Rate Variability</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#ffffff60', fontSize: 12 }}
                axisLine={{ stroke: '#ffffff20' }}
              />
              <YAxis 
                tick={{ fill: '#ffffff60', fontSize: 12 }}
                axisLine={{ stroke: '#ffffff20' }}
              />
              <Line 
                type="monotone" 
                dataKey="hrv" 
                stroke="#a855f7" 
                strokeWidth={2}
                dot={{ fill: '#a855f7', strokeWidth: 2, r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Sleep Pattern */}
      <Card className="bg-white/5 backdrop-blur-xl border border-purple-500/20">
        <CardHeader>
          <CardTitle className="text-white/80">Sleep & Energy Pattern</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#ffffff60', fontSize: 12 }}
                axisLine={{ stroke: '#ffffff20' }}
              />
              <YAxis 
                tick={{ fill: '#ffffff60', fontSize: 12 }}
                axisLine={{ stroke: '#ffffff20' }}
              />
              <Area 
                type="monotone" 
                dataKey="sleep" 
                stackId="1"
                stroke="#8b5cf6" 
                fill="#8b5cf6" 
                fillOpacity={0.3}
              />
              <Area 
                type="monotone" 
                dataKey="energy" 
                stackId="2"
                stroke="#a855f7" 
                fill="#a855f7" 
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};
