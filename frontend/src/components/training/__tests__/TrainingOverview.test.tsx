import React from 'react';
import { render, screen } from '@testing-library/react';
import { TrainingOverview } from '../TrainingOverview';

const mockTrainingData = {
  todaysWorkout: {
    id: 'w1',
    name: 'Upper Body Strength',
    duration: 45,
    exercises: [
      { name: 'Bench Press', sets: 3, reps: 8, weight: 100 },
      { name: 'Pull-ups', sets: 3, reps: 10, weight: 0 }
    ],
    completed: false
  },
  weeklyProgress: {
    workoutsCompleted: 3,
    workoutsPlanned: 5,
    totalDuration: 135,
    caloriesBurned: 850
  },
  upcomingWorkouts: [
    { id: 'w2', name: 'Lower Body', date: '2024-01-02' },
    { id: 'w3', name: 'Cardio', date: '2024-01-03' }
  ]
};

describe('TrainingOverview', () => {
  it('displays todays workout', () => {
    render(<TrainingOverview data={mockTrainingData} />);

    expect(screen.getByText('Upper Body Strength')).toBeInTheDocument();
    expect(screen.getByText('45 min')).toBeInTheDocument();
  });

  it('shows exercise list', () => {
    render(<TrainingOverview data={mockTrainingData} />);

    expect(screen.getByText('Bench Press')).toBeInTheDocument();
    expect(screen.getByText('Pull-ups')).toBeInTheDocument();
    expect(screen.getByText('3 x 8')).toBeInTheDocument();
    expect(screen.getByText('3 x 10')).toBeInTheDocument();
  });

  it('displays weekly progress', () => {
    render(<TrainingOverview data={mockTrainingData} />);

    expect(screen.getByText('3 / 5')).toBeInTheDocument();
    expect(screen.getByText('135 min')).toBeInTheDocument();
    expect(screen.getByText('850 cal')).toBeInTheDocument();
  });

  it('shows upcoming workouts', () => {
    render(<TrainingOverview data={mockTrainingData} />);

    expect(screen.getByText('Lower Body')).toBeInTheDocument();
    expect(screen.getByText('Cardio')).toBeInTheDocument();
  });

  it('indicates workout completion status', () => {
    render(<TrainingOverview data={mockTrainingData} />);

    expect(screen.getByText(/not completed/i)).toBeInTheDocument();
  });

  it('handles missing workout data', () => {
    const emptyData = {
      todaysWorkout: null,
      weeklyProgress: { workoutsCompleted: 0, workoutsPlanned: 0, totalDuration: 0, caloriesBurned: 0 },
      upcomingWorkouts: []
    };

    render(<TrainingOverview data={emptyData} />);

    expect(screen.getByText(/no workout scheduled/i)).toBeInTheDocument();
  });
});
