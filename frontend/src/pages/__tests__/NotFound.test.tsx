import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import NotFound from '../NotFound';

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('NotFound', () => {
  it('displays 404 error message', () => {
    renderWithRouter(<NotFound />);

    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText(/page not found/i)).toBeInTheDocument();
  });

  it('shows helpful message to user', () => {
    renderWithRouter(<NotFound />);

    expect(screen.getByText(/page you are looking for/i)).toBeInTheDocument();
  });

  it('has link to go back home', () => {
    renderWithRouter(<NotFound />);

    const homeLink = screen.getByRole('link', { name: /go home/i });
    expect(homeLink).toHaveAttribute('href', '/');
  });

  it('has accessible heading structure', () => {
    renderWithRouter(<NotFound />);

    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  it('includes navigation suggestions', () => {
    renderWithRouter(<NotFound />);

    expect(screen.getByText(/try these links/i)).toBeInTheDocument();
  });
});
