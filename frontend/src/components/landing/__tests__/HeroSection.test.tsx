import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { HeroSection } from '../HeroSection';

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('HeroSection', () => {
  it('renders main heading', () => {
    renderWithRouter(<HeroSection />);

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  it('displays call-to-action button', () => {
    renderWithRouter(<HeroSection />);

    expect(screen.getByRole('button', { name: /get started/i })).toBeInTheDocument();
  });

  it('shows hero description', () => {
    renderWithRouter(<HeroSection />);

    expect(screen.getByText(/AI-powered fitness/i)).toBeInTheDocument();
  });

  it('has accessible structure', () => {
    renderWithRouter(<HeroSection />);

    expect(screen.getByRole('banner')).toBeInTheDocument();
  });
});
