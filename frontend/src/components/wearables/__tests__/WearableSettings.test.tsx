import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WearableSettings } from '../WearableSettings';

const mockWearableData = {
  connectedDevices: [
    { id: '1', name: 'Apple Watch', type: 'smartwatch', connected: true },
    { id: '2', name: 'Fitbit Charge', type: 'fitness-tracker', connected: false }
  ],
  availableDevices: [
    { id: '3', name: 'Garmin Forerunner', type: 'gps-watch' }
  ]
};

describe('WearableSettings', () => {
  it('displays connected devices', () => {
    render(<WearableSettings data={mockWearableData} />);

    expect(screen.getByText('Apple Watch')).toBeInTheDocument();
    expect(screen.getByText('Fitbit Charge')).toBeInTheDocument();
  });

  it('shows device connection status', () => {
    render(<WearableSettings data={mockWearableData} />);

    expect(screen.getByText(/connected/i)).toBeInTheDocument();
    expect(screen.getByText(/disconnected/i)).toBeInTheDocument();
  });

  it('lists available devices for connection', () => {
    render(<WearableSettings data={mockWearableData} />);

    expect(screen.getByText('Garmin Forerunner')).toBeInTheDocument();
  });

  it('has connect button for available devices', () => {
    render(<WearableSettings data={mockWearableData} />);

    expect(screen.getByRole('button', { name: /connect/i })).toBeInTheDocument();
  });

  it('shows sync options', () => {
    render(<WearableSettings data={mockWearableData} />);

    expect(screen.getByText(/sync preferences/i)).toBeInTheDocument();
  });
});
