import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
} from '../card';

describe('Card Component', () => {
  describe('Card', () => {
    it('renders card container', () => {
      render(<Card>Card content</Card>);
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(<Card className="custom-card">Content</Card>);
      const card = screen.getByText('Content').parentElement;
      expect(card).toHaveClass('custom-card');
      expect(card).toHaveClass('rounded-lg', 'border', 'bg-card', 'text-card-foreground', 'shadow-sm');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(<Card ref={ref}>Card with ref</Card>);
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });

    it('handles click events', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Card onClick={handleClick}>Clickable card</Card>);
      const card = screen.getByText('Clickable card').parentElement;
      
      await user.click(card!);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('passes through other HTML attributes', () => {
      render(<Card data-testid="test-card" role="article">Content</Card>);
      const card = screen.getByTestId('test-card');
      expect(card).toHaveAttribute('role', 'article');
    });
  });

  describe('CardHeader', () => {
    it('renders header content', () => {
      render(
        <Card>
          <CardHeader>Header content</CardHeader>
        </Card>
      );
      expect(screen.getByText('Header content')).toBeInTheDocument();
    });

    it('applies correct styling', () => {
      render(
        <Card>
          <CardHeader data-testid="card-header">Header</CardHeader>
        </Card>
      );
      const header = screen.getByTestId('card-header');
      expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6');
    });

    it('applies custom className', () => {
      render(
        <Card>
          <CardHeader className="custom-header">Header</CardHeader>
        </Card>
      );
      const header = screen.getByText('Header').parentElement;
      expect(header).toHaveClass('custom-header');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(
        <Card>
          <CardHeader ref={ref}>Header</CardHeader>
        </Card>
      );
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('CardTitle', () => {
    it('renders title text', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
        </Card>
      );
      const title = screen.getByText('Card Title');
      expect(title).toBeInTheDocument();
      expect(title.tagName).toBe('H3');
    });

    it('applies correct styling', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
          </CardHeader>
        </Card>
      );
      const title = screen.getByText('Title');
      expect(title).toHaveClass('text-2xl', 'font-semibold', 'leading-none', 'tracking-tight');
    });

    it('applies custom className', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle className="custom-title">Title</CardTitle>
          </CardHeader>
        </Card>
      );
      const title = screen.getByText('Title');
      expect(title).toHaveClass('custom-title');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLParagraphElement>();
      render(
        <Card>
          <CardHeader>
            <CardTitle ref={ref}>Title</CardTitle>
          </CardHeader>
        </Card>
      );
      expect(ref.current).toBeInstanceOf(HTMLHeadingElement);
    });
  });

  describe('CardDescription', () => {
    it('renders description text', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Card description text</CardDescription>
          </CardHeader>
        </Card>
      );
      const description = screen.getByText('Card description text');
      expect(description).toBeInTheDocument();
      expect(description.tagName).toBe('P');
    });

    it('applies correct styling', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Description</CardDescription>
          </CardHeader>
        </Card>
      );
      const description = screen.getByText('Description');
      expect(description).toHaveClass('text-sm', 'text-muted-foreground');
    });

    it('applies custom className', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription className="custom-description">Description</CardDescription>
          </CardHeader>
        </Card>
      );
      const description = screen.getByText('Description');
      expect(description).toHaveClass('custom-description');
    });
  });

  describe('CardContent', () => {
    it('renders content', () => {
      render(
        <Card>
          <CardContent>Card content area</CardContent>
        </Card>
      );
      expect(screen.getByText('Card content area')).toBeInTheDocument();
    });

    it('applies correct styling', () => {
      render(
        <Card>
          <CardContent data-testid="card-content">Content</CardContent>
        </Card>
      );
      const content = screen.getByTestId('card-content');
      expect(content).toHaveClass('p-6', 'pt-0');
    });

    it('applies custom className', () => {
      render(
        <Card>
          <CardContent className="custom-content">Content</CardContent>
        </Card>
      );
      const content = screen.getByText('Content').parentElement;
      expect(content).toHaveClass('custom-content');
    });
  });

  describe('CardFooter', () => {
    it('renders footer content', () => {
      render(
        <Card>
          <CardFooter>Footer content</CardFooter>
        </Card>
      );
      expect(screen.getByText('Footer content')).toBeInTheDocument();
    });

    it('applies correct styling', () => {
      render(
        <Card>
          <CardFooter data-testid="card-footer">Footer</CardFooter>
        </Card>
      );
      const footer = screen.getByTestId('card-footer');
      expect(footer).toHaveClass('flex', 'items-center', 'p-6', 'pt-0');
    });

    it('applies custom className', () => {
      render(
        <Card>
          <CardFooter className="custom-footer">Footer</CardFooter>
        </Card>
      );
      const footer = screen.getByText('Footer').parentElement;
      expect(footer).toHaveClass('custom-footer');
    });
  });

  describe('Complete Card composition', () => {
    it('renders all card components together', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Full Card Example</CardTitle>
            <CardDescription>This is a complete card</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Main content goes here</p>
          </CardContent>
          <CardFooter>
            <button>Action</button>
          </CardFooter>
        </Card>
      );

      expect(screen.getByText('Full Card Example')).toBeInTheDocument();
      expect(screen.getByText('This is a complete card')).toBeInTheDocument();
      expect(screen.getByText('Main content goes here')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
    });

    it('maintains proper component hierarchy', () => {
      render(
        <Card data-testid="card">
          <CardHeader data-testid="header">
            <CardTitle>Title</CardTitle>
          </CardHeader>
          <CardContent data-testid="content">Content</CardContent>
          <CardFooter data-testid="footer">Footer</CardFooter>
        </Card>
      );

      const card = screen.getByTestId('card');
      const header = screen.getByTestId('header');
      const content = screen.getByTestId('content');
      const footer = screen.getByTestId('footer');

      expect(card).toContainElement(header);
      expect(card).toContainElement(content);
      expect(card).toContainElement(footer);
    });

    it('supports nested cards', () => {
      render(
        <Card data-testid="parent-card">
          <CardContent>
            <Card data-testid="nested-card">
              <CardContent>Nested content</CardContent>
            </Card>
          </CardContent>
        </Card>
      );

      const parentCard = screen.getByTestId('parent-card');
      const nestedCard = screen.getByTestId('nested-card');
      
      expect(parentCard).toContainElement(nestedCard);
      expect(screen.getByText('Nested content')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('supports ARIA attributes', () => {
      render(
        <Card role="article" aria-label="Product card">
          <CardHeader>
            <CardTitle id="card-title">Product</CardTitle>
            <CardDescription id="card-desc">Description</CardDescription>
          </CardHeader>
          <CardContent aria-describedby="card-desc">Content</CardContent>
        </Card>
      );

      const card = screen.getByRole('article', { name: 'Product card' });
      expect(card).toBeInTheDocument();
      
      const content = screen.getByText('Content').parentElement;
      expect(content).toHaveAttribute('aria-describedby', 'card-desc');
    });

    it('maintains semantic HTML structure', () => {
      const { container } = render(
        <Card>
          <CardHeader>
            <CardTitle>Semantic Title</CardTitle>
            <CardDescription>Semantic Description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Semantic paragraph</p>
          </CardContent>
        </Card>
      );

      const heading = container.querySelector('h3');
      const paragraph = container.querySelector('p');
      
      expect(heading).toHaveTextContent('Semantic Title');
      expect(paragraph).toHaveTextContent('Semantic Description');
    });
  });
});