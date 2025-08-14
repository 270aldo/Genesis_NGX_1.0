import React from 'react';
import { render, screen } from '@testing-library/react';
import { Badge } from '../badge';

describe('Badge Component', () => {
  it('renders badge with text', () => {
    render(<Badge>Badge text</Badge>);
    expect(screen.getByText('Badge text')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Badge className="custom-badge">Badge</Badge>);
    const badge = screen.getByText('Badge');
    expect(badge).toHaveClass('custom-badge');
  });

  it('renders different variants', () => {
    const { rerender } = render(<Badge variant="default">Default</Badge>);
    expect(screen.getByText('Default')).toBeInTheDocument();

    rerender(<Badge variant="secondary">Secondary</Badge>);
    expect(screen.getByText('Secondary')).toBeInTheDocument();

    rerender(<Badge variant="destructive">Destructive</Badge>);
    expect(screen.getByText('Destructive')).toBeInTheDocument();

    rerender(<Badge variant="outline">Outline</Badge>);
    expect(screen.getByText('Outline')).toBeInTheDocument();
  });

  it('applies base styling classes', () => {
    render(<Badge>Styled badge</Badge>);
    const badge = screen.getByText('Styled badge');
    expect(badge).toHaveClass(
      'inline-flex',
      'items-center',
      'rounded-full',
      'border',
      'px-2.5',
      'py-0.5',
      'text-xs',
      'font-semibold',
      'transition-colors',
      'focus:outline-none',
      'focus:ring-2',
      'focus:ring-ring',
      'focus:ring-offset-2'
    );
  });

  it('applies default variant styling', () => {
    render(<Badge>Default badge</Badge>);
    const badge = screen.getByText('Default badge');
    expect(badge).toHaveClass('border-transparent', 'bg-primary', 'text-primary-foreground', 'hover:bg-primary/80');
  });

  it('applies secondary variant styling', () => {
    render(<Badge variant="secondary">Secondary badge</Badge>);
    const badge = screen.getByText('Secondary badge');
    expect(badge).toHaveClass('border-transparent', 'bg-secondary', 'text-secondary-foreground', 'hover:bg-secondary/80');
  });

  it('applies destructive variant styling', () => {
    render(<Badge variant="destructive">Destructive badge</Badge>);
    const badge = screen.getByText('Destructive badge');
    expect(badge).toHaveClass('border-transparent', 'bg-destructive', 'text-destructive-foreground', 'hover:bg-destructive/80');
  });

  it('applies outline variant styling', () => {
    render(<Badge variant="outline">Outline badge</Badge>);
    const badge = screen.getByText('Outline badge');
    expect(badge).toHaveClass('text-foreground');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLDivElement>();
    render(<Badge ref={ref}>Badge with ref</Badge>);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('passes through HTML attributes', () => {
    render(
      <Badge data-testid="test-badge" role="status" aria-label="Status badge">
        Status
      </Badge>
    );

    const badge = screen.getByTestId('test-badge');
    expect(badge).toHaveAttribute('role', 'status');
    expect(badge).toHaveAttribute('aria-label', 'Status badge');
  });

  it('supports children as ReactNode', () => {
    render(
      <Badge>
        <span>Icon</span>
        <span>Text</span>
      </Badge>
    );

    expect(screen.getByText('Icon')).toBeInTheDocument();
    expect(screen.getByText('Text')).toBeInTheDocument();
  });

  it('handles empty content', () => {
    render(<Badge />);
    const badge = screen.getByRole('generic');
    expect(badge).toBeInTheDocument();
    expect(badge).toBeEmptyDOMElement();
  });

  it('handles numeric content', () => {
    render(<Badge>{42}</Badge>);
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('supports focus interaction', () => {
    render(<Badge tabIndex={0}>Focusable badge</Badge>);
    const badge = screen.getByText('Focusable badge');

    badge.focus();
    expect(badge).toHaveFocus();
  });

  it('combines variants with custom classes correctly', () => {
    render(
      <Badge variant="outline" className="custom-outline">
        Custom outline
      </Badge>
    );

    const badge = screen.getByText('Custom outline');
    expect(badge).toHaveClass('text-foreground'); // variant class
    expect(badge).toHaveClass('custom-outline'); // custom class
  });

  it('maintains styling with long text content', () => {
    const longText = 'This is a very long badge text that might wrap or overflow';
    render(<Badge>{longText}</Badge>);

    const badge = screen.getByText(longText);
    expect(badge).toHaveClass('inline-flex', 'items-center');
  });

  it('renders consistently across different variants', () => {
    const variants = ['default', 'secondary', 'destructive', 'outline'] as const;

    variants.forEach((variant) => {
      const { unmount } = render(<Badge variant={variant}>Test {variant}</Badge>);

      const badge = screen.getByText(`Test ${variant}`);
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('inline-flex', 'items-center', 'rounded-full');

      unmount();
    });
  });

  describe('Accessibility', () => {
    it('supports ARIA attributes for status badges', () => {
      render(
        <Badge role="status" aria-live="polite" aria-label="Notification count">
          3
        </Badge>
      );

      const badge = screen.getByRole('status');
      expect(badge).toHaveAttribute('aria-live', 'polite');
      expect(badge).toHaveAttribute('aria-label', 'Notification count');
    });

    it('can be used as a live region', () => {
      const TestComponent = () => {
        const [count, setCount] = React.useState(0);

        return (
          <div>
            <button onClick={() => setCount(c => c + 1)}>Increment</button>
            <Badge role="status" aria-live="polite" aria-label={`${count} notifications`}>
              {count}
            </Badge>
          </div>
        );
      };

      render(<TestComponent />);

      const badge = screen.getByRole('status');
      expect(badge).toHaveAttribute('aria-live', 'polite');
      expect(badge).toHaveTextContent('0');
    });

    it('provides semantic meaning with proper ARIA labels', () => {
      render(
        <Badge variant="destructive" role="status" aria-label="Error status">
          Error
        </Badge>
      );

      const badge = screen.getByLabelText('Error status');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('bg-destructive');
    });
  });

  describe('Visual states', () => {
    it('applies hover states correctly', () => {
      render(<Badge>Hoverable badge</Badge>);
      const badge = screen.getByText('Hoverable badge');
      expect(badge).toHaveClass('hover:bg-primary/80');
    });

    it('applies focus states correctly', () => {
      render(<Badge>Focusable badge</Badge>);
      const badge = screen.getByText('Focusable badge');
      expect(badge).toHaveClass(
        'focus:outline-none',
        'focus:ring-2',
        'focus:ring-ring',
        'focus:ring-offset-2'
      );
    });

    it('supports transition effects', () => {
      render(<Badge>Animated badge</Badge>);
      const badge = screen.getByText('Animated badge');
      expect(badge).toHaveClass('transition-colors');
    });
  });

  describe('Use cases', () => {
    it('works as a notification badge', () => {
      render(
        <div className="relative">
          <button>Messages</button>
          <Badge
            className="absolute -top-2 -right-2"
            variant="destructive"
            aria-label="5 unread messages"
          >
            5
          </Badge>
        </div>
      );

      const badge = screen.getByLabelText('5 unread messages');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveTextContent('5');
    });

    it('works as a status indicator', () => {
      render(
        <div className="flex items-center gap-2">
          <span>Server Status</span>
          <Badge variant="secondary" role="status">
            Online
          </Badge>
        </div>
      );

      const badge = screen.getByRole('status');
      expect(badge).toHaveTextContent('Online');
      expect(badge).toHaveClass('bg-secondary');
    });

    it('works as a category tag', () => {
      render(
        <div className="flex gap-2">
          {['React', 'TypeScript', 'Testing'].map(tag => (
            <Badge key={tag} variant="outline">
              {tag}
            </Badge>
          ))}
        </div>
      );

      expect(screen.getByText('React')).toBeInTheDocument();
      expect(screen.getByText('TypeScript')).toBeInTheDocument();
      expect(screen.getByText('Testing')).toBeInTheDocument();
    });
  });
});
