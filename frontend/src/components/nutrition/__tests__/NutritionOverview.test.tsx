import React from 'react';
import { render, screen } from '@testing-library/react';
import { NutritionOverview } from '../NutritionOverview';

const mockNutritionData = {
  calories: { consumed: 1800, target: 2000, remaining: 200 },
  macros: {
    protein: { consumed: 120, target: 150, percentage: 80 },
    carbs: { consumed: 180, target: 250, percentage: 72 },
    fat: { consumed: 80, target: 90, percentage: 89 }
  },
  water: { consumed: 6, target: 8, percentage: 75 },
  meals: [
    { id: '1', name: 'Breakfast', calories: 450, time: '08:00' },
    { id: '2', name: 'Lunch', calories: 650, time: '12:30' },
    { id: '3', name: 'Dinner', calories: 700, time: '19:00' }
  ]
};

describe('NutritionOverview', () => {
  it('displays calorie information', () => {
    render(<NutritionOverview data={mockNutritionData} />);

    expect(screen.getByText('1,800')).toBeInTheDocument();
    expect(screen.getByText('2,000')).toBeInTheDocument();
    expect(screen.getByText(/calories/i)).toBeInTheDocument();
  });

  it('shows macro breakdown', () => {
    render(<NutritionOverview data={mockNutritionData} />);

    expect(screen.getByText('120g')).toBeInTheDocument();
    expect(screen.getByText('180g')).toBeInTheDocument();
    expect(screen.getByText('80g')).toBeInTheDocument();
    expect(screen.getByText(/protein/i)).toBeInTheDocument();
    expect(screen.getByText(/carbs/i)).toBeInTheDocument();
    expect(screen.getByText(/fat/i)).toBeInTheDocument();
  });

  it('displays water intake', () => {
    render(<NutritionOverview data={mockNutritionData} />);

    expect(screen.getByText('6 / 8')).toBeInTheDocument();
    expect(screen.getByText(/water/i)).toBeInTheDocument();
  });

  it('lists meals', () => {
    render(<NutritionOverview data={mockNutritionData} />);

    expect(screen.getByText('Breakfast')).toBeInTheDocument();
    expect(screen.getByText('Lunch')).toBeInTheDocument();
    expect(screen.getByText('Dinner')).toBeInTheDocument();
  });

  it('shows calorie progress bar', () => {
    render(<NutritionOverview data={mockNutritionData} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '90'); // 1800/2000 * 100
  });
});
