import React from 'react';
import { render, screen } from '@testing-library/react';
import { Alert, AlertTitle, AlertDescription } from '../alert';
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

describe('Alert Component', () => {
  describe('Alert', () => {
    it('renders alert container', () => {
      render(<Alert>Alert content</Alert>);
      expect(screen.getByText('Alert content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(<Alert className="custom-alert">Alert</Alert>);
      const alert = screen.getByText('Alert').parentElement;
      expect(alert).toHaveClass('custom-alert');
    });

    it('applies base styling classes', () => {
      render(<Alert data-testid="alert">Alert content</Alert>);
      const alert = screen.getByTestId('alert');
      expect(alert).toHaveClass(
        'relative',
        'w-full',
        'rounded-lg',
        'border',
        'p-4',
        '[&>svg~*]:pl-7',
        '[&>svg+div]:translate-y-[-3px]',
        '[&>svg]:absolute',
        '[&>svg]:left-4',
        '[&>svg]:top-4',
        '[&>svg]:text-foreground'
      );
    });

    it('renders default variant styling', () => {
      render(<Alert data-testid="alert">Default alert</Alert>);
      const alert = screen.getByTestId('alert');
      expect(alert).toHaveClass('bg-background', 'text-foreground');
    });

    it('renders destructive variant styling', () => {
      render(
        <Alert variant="destructive" data-testid="alert">
          Destructive alert
        </Alert>
      );
      const alert = screen.getByTestId('alert');
      expect(alert).toHaveClass(
        'border-destructive/50',
        'text-destructive',
        'dark:border-destructive',
        '[&>svg]:text-destructive'
      );
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(<Alert ref={ref}>Alert with ref</Alert>);
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });

    it('passes through HTML attributes', () => {
      render(
        <Alert
          data-testid="test-alert"
          role="alert"
          aria-label="Important notification"
        >
          Alert content
        </Alert>
      );

      const alert = screen.getByTestId('test-alert');
      expect(alert).toHaveAttribute('role', 'alert');
      expect(alert).toHaveAttribute('aria-label', 'Important notification');
    });

    it('supports icon placement', () => {
      render(
        <Alert>
          <AlertCircle className="h-4 w-4" />
          Alert with icon
        </Alert>
      );

      expect(screen.getByText('Alert with icon')).toBeInTheDocument();
      // SVG should be positioned absolutely
      const alert = screen.getByText('Alert with icon').parentElement;
      expect(alert).toHaveClass('[&>svg]:absolute', '[&>svg]:left-4', '[&>svg]:top-4');
    });
  });

  describe('AlertTitle', () => {
    it('renders title text', () => {
      render(
        <Alert>
          <AlertTitle>Alert Title</AlertTitle>
        </Alert>
      );

      const title = screen.getByText('Alert Title');
      expect(title).toBeInTheDocument();
      expect(title.tagName).toBe('H5');
    });

    it('applies correct styling', () => {
      render(
        <Alert>
          <AlertTitle>Styled Title</AlertTitle>
        </Alert>
      );

      const title = screen.getByText('Styled Title');
      expect(title).toHaveClass('mb-1', 'font-medium', 'leading-none', 'tracking-tight');
    });

    it('applies custom className', () => {
      render(
        <Alert>
          <AlertTitle className="custom-title">Title</AlertTitle>
        </Alert>
      );

      const title = screen.getByText('Title');
      expect(title).toHaveClass('custom-title');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLParagraphElement>();
      render(
        <Alert>
          <AlertTitle ref={ref}>Title</AlertTitle>
        </Alert>
      );

      expect(ref.current).toBeInstanceOf(HTMLHeadingElement);
    });

    it('supports accessibility attributes', () => {
      render(
        <Alert>
          <AlertTitle id="alert-title" aria-level={2}>
            Accessible Title
          </AlertTitle>
        </Alert>
      );

      const title = screen.getByText('Accessible Title');
      expect(title).toHaveAttribute('id', 'alert-title');
      expect(title).toHaveAttribute('aria-level', '2');
    });
  });

  describe('AlertDescription', () => {
    it('renders description text', () => {
      render(
        <Alert>
          <AlertDescription>Alert description text</AlertDescription>
        </Alert>
      );

      const description = screen.getByText('Alert description text');
      expect(description).toBeInTheDocument();
      expect(description.tagName).toBe('DIV');
    });

    it('applies correct styling', () => {
      render(
        <Alert>
          <AlertDescription>Description</AlertDescription>
        </Alert>
      );

      const description = screen.getByText('Description');
      expect(description).toHaveClass('text-sm', '[&_p]:leading-relaxed');
    });

    it('applies custom className', () => {
      render(
        <Alert>
          <AlertDescription className="custom-description">
            Description
          </AlertDescription>
        </Alert>
      );

      const description = screen.getByText('Description');
      expect(description).toHaveClass('custom-description');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(
        <Alert>
          <AlertDescription ref={ref}>Description</AlertDescription>
        </Alert>
      );

      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });

    it('supports rich content', () => {
      render(
        <Alert>
          <AlertDescription>
            <p>First paragraph</p>
            <p>Second paragraph</p>
            <strong>Bold text</strong>
          </AlertDescription>
        </Alert>
      );

      expect(screen.getByText('First paragraph')).toBeInTheDocument();
      expect(screen.getByText('Second paragraph')).toBeInTheDocument();
      expect(screen.getByText('Bold text')).toBeInTheDocument();
    });

    it('handles paragraph spacing', () => {
      render(
        <Alert>
          <AlertDescription>
            <p>Paragraph with relaxed leading</p>
          </AlertDescription>
        </Alert>
      );

      const description = screen.getByText('Paragraph with relaxed leading').parentElement;
      expect(description).toHaveClass('[&_p]:leading-relaxed');
    });
  });

  describe('Complete Alert composition', () => {
    it('renders alert with title and description', () => {
      render(
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Complete Alert</AlertTitle>
          <AlertDescription>
            This alert has both title and description
          </AlertDescription>
        </Alert>
      );

      expect(screen.getByText('Complete Alert')).toBeInTheDocument();
      expect(screen.getByText('This alert has both title and description')).toBeInTheDocument();
    });

    it('maintains proper component hierarchy', () => {
      render(
        <Alert data-testid="alert">
          <AlertTitle data-testid="alert-title">Title</AlertTitle>
          <AlertDescription data-testid="alert-description">
            Description
          </AlertDescription>
        </Alert>
      );

      const alert = screen.getByTestId('alert');
      const title = screen.getByTestId('alert-title');
      const description = screen.getByTestId('alert-description');

      expect(alert).toContainElement(title);
      expect(alert).toContainElement(description);
    });

    it('works with different icon types', () => {
      const icons = [
        { Icon: CheckCircle, name: 'success' },
        { Icon: AlertTriangle, name: 'warning' },
        { Icon: AlertCircle, name: 'error' },
        { Icon: Info, name: 'info' }
      ];

      icons.forEach(({ Icon, name }) => {
        const { unmount } = render(
          <Alert data-testid={`${name}-alert`}>
            <Icon className="h-4 w-4" />
            <AlertTitle>{name} Alert</AlertTitle>
            <AlertDescription>{name} message</AlertDescription>
          </Alert>
        );

        expect(screen.getByText(`${name} Alert`)).toBeInTheDocument();
        expect(screen.getByText(`${name} message`)).toBeInTheDocument();

        unmount();
      });
    });

    it('supports variants with complete composition', () => {
      const { rerender } = render(
        <Alert variant="default">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Default Alert</AlertTitle>
          <AlertDescription>Default message</AlertDescription>
        </Alert>
      );

      expect(screen.getByText('Default Alert')).toBeInTheDocument();

      rerender(
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error Alert</AlertTitle>
          <AlertDescription>Error message</AlertDescription>
        </Alert>
      );

      expect(screen.getByText('Error Alert')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('supports proper ARIA labeling', () => {
      render(
        <Alert
          role="alert"
          aria-labelledby="alert-title"
          aria-describedby="alert-description"
        >
          <AlertTitle id="alert-title">Accessible Alert</AlertTitle>
          <AlertDescription id="alert-description">
            This alert follows accessibility guidelines
          </AlertDescription>
        </Alert>
      );

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-labelledby', 'alert-title');
      expect(alert).toHaveAttribute('aria-describedby', 'alert-description');
    });

    it('provides semantic meaning with alert role', () => {
      render(
        <Alert role="alert">
          <AlertTitle>Important</AlertTitle>
          <AlertDescription>This requires immediate attention</AlertDescription>
        </Alert>
      );

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });

    it('supports different alert types with appropriate roles', () => {
      const alertTypes = [
        { role: 'alert', title: 'Error', description: 'Something went wrong' },
        { role: 'status', title: 'Success', description: 'Action completed' },
        { role: 'note', title: 'Info', description: 'Additional information' }
      ];

      alertTypes.forEach(({ role, title, description }) => {
        const { unmount } = render(
          <Alert role={role as any} data-testid={`${role}-alert`}>
            <AlertTitle>{title}</AlertTitle>
            <AlertDescription>{description}</AlertDescription>
          </Alert>
        );

        const alert = screen.getByTestId(`${role}-alert`);
        expect(alert).toHaveAttribute('role', role);

        unmount();
      });
    });

    it('supports live regions for dynamic alerts', () => {
      render(
        <Alert role="alert" aria-live="assertive" aria-atomic="true">
          <AlertTitle>Live Alert</AlertTitle>
          <AlertDescription>This will be announced immediately</AlertDescription>
        </Alert>
      );

      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'assertive');
      expect(alert).toHaveAttribute('aria-atomic', 'true');
    });
  });

  describe('Visual variants and styling', () => {
    it('applies destructive styling consistently', () => {
      render(
        <Alert variant="destructive" data-testid="destructive-alert">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>Something went wrong</AlertDescription>
        </Alert>
      );

      const alert = screen.getByTestId('destructive-alert');
      expect(alert).toHaveClass(
        'border-destructive/50',
        'text-destructive',
        '[&>svg]:text-destructive'
      );
    });

    it('handles icon positioning with text content', () => {
      render(
        <Alert data-testid="icon-alert">
          <CheckCircle className="h-4 w-4" />
          <div>Content next to icon</div>
        </Alert>
      );

      const alert = screen.getByTestId('icon-alert');
      expect(alert).toHaveClass('[&>svg~*]:pl-7', '[&>svg+div]:translate-y-[-3px]');
    });
  });

  describe('Use cases', () => {
    it('works as an error alert', () => {
      render(
        <Alert variant="destructive" role="alert">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Failed to save changes. Please try again.
          </AlertDescription>
        </Alert>
      );

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Failed to save changes. Please try again.')).toBeInTheDocument();
    });

    it('works as a success notification', () => {
      render(
        <Alert role="status">
          <CheckCircle className="h-4 w-4" />
          <AlertTitle>Success</AlertTitle>
          <AlertDescription>Your changes have been saved successfully.</AlertDescription>
        </Alert>
      );

      const alert = screen.getByRole('status');
      expect(alert).toBeInTheDocument();
      expect(screen.getByText('Success')).toBeInTheDocument();
    });

    it('works as an informational alert', () => {
      render(
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Information</AlertTitle>
          <AlertDescription>
            New features are available in this update.
          </AlertDescription>
        </Alert>
      );

      expect(screen.getByText('Information')).toBeInTheDocument();
      expect(screen.getByText('New features are available in this update.')).toBeInTheDocument();
    });

    it('works without title for simple alerts', () => {
      render(
        <Alert>
          <AlertDescription>Simple alert message without title</AlertDescription>
        </Alert>
      );

      expect(screen.getByText('Simple alert message without title')).toBeInTheDocument();
    });
  });
});
