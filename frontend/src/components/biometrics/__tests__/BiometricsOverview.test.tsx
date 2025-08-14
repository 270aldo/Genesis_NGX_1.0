import React from 'react';
import { render, screen } from '@testing-library/react';
import { BiometricsOverview } from '../BiometricsOverview';

const mockBiometricsData = {
  heartRate: { current: 72, avg: 68, trend: 'stable' },
  hrv: { current: 45, avg: 42, trend: 'improving' },
  sleep: { hours: 7.5, quality: 85, trend: 'good' },
  recovery: { score: 78, status: 'ready' }
};

describe('BiometricsOverview', () => {
  it('displays heart rate data', () => {
    render(<BiometricsOverview data={mockBiometricsData} />);

    expect(screen.getByText('72')).toBeInTheDocument();
    expect(screen.getByText(/heart rate/i)).toBeInTheDocument();
  });

  it('shows HRV information', () => {
    render(<BiometricsOverview data={mockBiometricsData} />);

    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText(/hrv/i)).toBeInTheDocument();
  });

  it('displays sleep data', () => {
    render(<BiometricsOverview data={mockBiometricsData} />);

    expect(screen.getByText('7.5h')).toBeInTheDocument();
    expect(screen.getByText(/sleep/i)).toBeInTheDocument();
  });

  it('shows recovery status', () => {
    render(<BiometricsOverview data={mockBiometricsData} />);

    expect(screen.getByText('78')).toBeInTheDocument();
    expect(screen.getByText(/recovery/i)).toBeInTheDocument();
  });

  it('handles missing data gracefully', () => {
    render(<BiometricsOverview data={{}} />);

    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });
});
