import React from 'react';
import { render, screen } from '@testing-library/react';
import { ProgressCharts } from '../ProgressCharts';

// Mock Chart.js components
jest.mock('chart.js', () => ({
  Chart: jest.fn(),
  CategoryScale: jest.fn(),
  LinearScale: jest.fn(),
  PointElement: jest.fn(),
  LineElement: jest.fn(),
  Title: jest.fn(),
  Tooltip: jest.fn(),
  Legend: jest.fn()
}));

jest.mock('react-chartjs-2', () => ({
  Line: ({ data, options }: any) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data)}>
      Chart: {data.datasets[0].label}
    </div>
  ),
  Bar: ({ data, options }: any) => (
    <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)}>
      Chart: {data.datasets[0].label}
    </div>
  )
}));

const mockProgressData = {
  weight: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    data: [180, 178, 176, 175],
    unit: 'lbs'
  },
  strength: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    data: [135, 140, 145, 150],
    unit: 'lbs',
    exercise: 'Bench Press'
  },
  bodyFat: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    data: [18, 17.5, 17, 16.5],
    unit: '%'
  }
};

describe('ProgressCharts', () => {
  it('renders weight progress chart', () => {
    render(<ProgressCharts data={mockProgressData} />);

    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    expect(screen.getByText(/weight/i)).toBeInTheDocument();
  });

  it('displays strength progress', () => {
    render(<ProgressCharts data={mockProgressData} />);

    expect(screen.getByText(/strength/i)).toBeInTheDocument();
    expect(screen.getByText('Bench Press')).toBeInTheDocument();
  });

  it('shows body fat percentage chart', () => {
    render(<ProgressCharts data={mockProgressData} />);

    expect(screen.getByText(/body fat/i)).toBeInTheDocument();
  });

  it('handles empty data', () => {
    const emptyData = {
      weight: { labels: [], data: [], unit: 'lbs' },
      strength: { labels: [], data: [], unit: 'lbs', exercise: 'Bench Press' },
      bodyFat: { labels: [], data: [], unit: '%' }
    };

    render(<ProgressCharts data={emptyData} />);

    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('displays trend indicators', () => {
    render(<ProgressCharts data={mockProgressData} />);

    expect(screen.getByText(/trending down/i)).toBeInTheDocument(); // Weight loss
    expect(screen.getByText(/trending up/i)).toBeInTheDocument(); // Strength gain
  });
});
