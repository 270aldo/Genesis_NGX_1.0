
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { LineChart, Line, XAxis, YAxis, AreaChart, Area } from 'recharts';
import { useProgressStore } from '@/store/progressStore';
import { format, parseISO } from 'date-fns';

export const ProgressCharts: React.FC = () => {
  const { getFilteredData } = useProgressStore();
  const data = getFilteredData();

  const chartConfig = {
    weight: {
      label: "Weight",
      color: "#8b5cf6",
    },
    bodyFat: {
      label: "Body Fat %",
      color: "#ef4444",
    },
    muscleMass: {
      label: "Muscle Mass",
      color: "#10b981",
    },
  };

  const formattedData = data.map(entry => ({
    ...entry,
    formattedDate: format(parseISO(entry.date), 'MMM dd'),
  }));

  return (
    <div className="space-y-6">
      {/* Weight Progress */}
      <Card className="bg-white/5 border-purple-500/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            Weight Progress
            <span className="text-sm font-normal text-white/60">
              (-2.0kg in 3 months)
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="h-[300px]">
            <AreaChart data={formattedData}>
              <XAxis dataKey="formattedDate" />
              <YAxis domain={['dataMin - 1', 'dataMax + 1']} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Area
                type="monotone"
                dataKey="weight"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.1}
                strokeWidth={2}
              />
            </AreaChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Body Composition */}
      <Card className="bg-white/5 border-purple-500/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Body Composition</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="h-[300px]">
            <LineChart data={formattedData}>
              <XAxis dataKey="formattedDate" />
              <YAxis />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                type="monotone"
                dataKey="bodyFat"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="muscleMass"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Body Measurements */}
      <Card className="bg-white/5 border-purple-500/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-white">Body Measurements</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig} className="h-[300px]">
            <LineChart data={formattedData}>
              <XAxis dataKey="formattedDate" />
              <YAxis />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                type="monotone"
                dataKey="waist"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', strokeWidth: 2, r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="chest"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="arms"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ fill: '#06b6d4', strokeWidth: 2, r: 3 }}
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  );
};
