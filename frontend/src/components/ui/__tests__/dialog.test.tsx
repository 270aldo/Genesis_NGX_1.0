import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '../dialog';

describe('Dialog Component', () => {
  describe('Dialog', () => {
    it('renders dialog container', () => {
      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Dialog</button>
          </DialogTrigger>
          <DialogContent>Dialog content</DialogContent>
        </Dialog>
      );

      expect(screen.getByRole('button', { name: /open dialog/i })).toBeInTheDocument();
    });

    it('opens dialog when trigger is clicked', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Dialog</button>
          </DialogTrigger>
          <DialogContent>Dialog content</DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open dialog/i }));

      await waitFor(() => {
        expect(screen.getByText('Dialog content')).toBeInTheDocument();
      });
    });

    it('closes dialog when overlay is clicked', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Dialog</button>
          </DialogTrigger>
          <DialogContent>Dialog content</DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open dialog/i }));

      await waitFor(() => {
        expect(screen.getByText('Dialog content')).toBeInTheDocument();
      });

      // Click the overlay (backdrop)
      const overlay = screen.getByRole('dialog').parentElement;
      if (overlay) {
        fireEvent.click(overlay);

        await waitFor(() => {
          expect(screen.queryByText('Dialog content')).not.toBeInTheDocument();
        });
      }
    });

    it('closes dialog when escape key is pressed', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Dialog</button>
          </DialogTrigger>
          <DialogContent>Dialog content</DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open dialog/i }));

      await waitFor(() => {
        expect(screen.getByText('Dialog content')).toBeInTheDocument();
      });

      await user.keyboard('{Escape}');

      await waitFor(() => {
        expect(screen.queryByText('Dialog content')).not.toBeInTheDocument();
      });
    });

    it('supports controlled state', async () => {
      const TestComponent = () => {
        const [open, setOpen] = React.useState(false);

        return (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <button>Open Dialog</button>
            </DialogTrigger>
            <DialogContent>
              <p>Controlled dialog</p>
              <button onClick={() => setOpen(false)}>Close</button>
            </DialogContent>
          </Dialog>
        );
      };

      const user = userEvent.setup();

      render(<TestComponent />);

      await user.click(screen.getByRole('button', { name: /open dialog/i }));

      await waitFor(() => {
        expect(screen.getByText('Controlled dialog')).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /close/i }));

      await waitFor(() => {
        expect(screen.queryByText('Controlled dialog')).not.toBeInTheDocument();
      });
    });
  });

  describe('DialogTrigger', () => {
    it('renders trigger element', () => {
      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Trigger</button>
          </DialogTrigger>
          <DialogContent>Content</DialogContent>
        </Dialog>
      );

      expect(screen.getByRole('button', { name: /trigger/i })).toBeInTheDocument();
    });

    it('has correct accessibility attributes', () => {
      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Dialog</button>
          </DialogTrigger>
          <DialogContent>Content</DialogContent>
        </Dialog>
      );

      const trigger = screen.getByRole('button', { name: /open dialog/i });
      expect(trigger).toHaveAttribute('aria-haspopup', 'dialog');
    });
  });

  describe('DialogContent', () => {
    it('renders with proper role and attributes', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>Dialog content</DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const dialog = screen.getByRole('dialog');
        expect(dialog).toBeInTheDocument();
        expect(dialog).toHaveAttribute('aria-modal', 'true');
      });
    });

    it('focuses content when opened', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <input data-testid="dialog-input" />
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const dialog = screen.getByRole('dialog');
        expect(dialog).toHaveFocus();
      });
    });

    it('traps focus within dialog', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <input data-testid="first-input" />
            <input data-testid="second-input" />
            <button data-testid="dialog-button">Button</button>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      // Tab through focusable elements
      await user.tab();
      expect(screen.getByTestId('first-input')).toHaveFocus();

      await user.tab();
      expect(screen.getByTestId('second-input')).toHaveFocus();

      await user.tab();
      expect(screen.getByTestId('dialog-button')).toHaveFocus();

      // Tab again should cycle back to first focusable element
      await user.tab();
      expect(screen.getByTestId('first-input')).toHaveFocus();
    });

    it('applies custom className', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent className="custom-dialog">Content</DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const dialog = screen.getByRole('dialog');
        expect(dialog).toHaveClass('custom-dialog');
      });
    });
  });

  describe('DialogHeader', () => {
    it('renders header content', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>Header content</DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        expect(screen.getByText('Header content')).toBeInTheDocument();
      });
    });

    it('applies correct styling', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader data-testid="dialog-header">Header</DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const header = screen.getByTestId('dialog-header');
        expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'text-center', 'sm:text-left');
      });
    });
  });

  describe('DialogTitle', () => {
    it('renders title as heading', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent aria-labelledby="dialog-title">
            <DialogHeader>
              <DialogTitle id="dialog-title">Dialog Title</DialogTitle>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const title = screen.getByText('Dialog Title');
        expect(title).toBeInTheDocument();
        expect(title.tagName).toBe('H2');
      });
    });

    it('provides accessible labeling for dialog', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent aria-labelledby="dialog-title">
            <DialogHeader>
              <DialogTitle id="dialog-title">Accessible Title</DialogTitle>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const dialog = screen.getByRole('dialog', { name: /accessible title/i });
        expect(dialog).toBeInTheDocument();
      });
    });

    it('applies correct styling', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Styled Title</DialogTitle>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const title = screen.getByText('Styled Title');
        expect(title).toHaveClass('text-lg', 'font-semibold', 'leading-none', 'tracking-tight');
      });
    });
  });

  describe('DialogDescription', () => {
    it('renders description text', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent aria-describedby="dialog-description">
            <DialogHeader>
              <DialogDescription id="dialog-description">
                This is a description
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        expect(screen.getByText('This is a description')).toBeInTheDocument();
      });
    });

    it('provides accessible description for dialog', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent aria-describedby="dialog-description">
            <DialogHeader>
              <DialogDescription id="dialog-description">
                Accessible description
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const dialog = screen.getByRole('dialog');
        expect(dialog).toHaveAttribute('aria-describedby', 'dialog-description');
      });
    });

    it('applies correct styling', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogDescription>Description text</DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const description = screen.getByText('Description text');
        expect(description).toHaveClass('text-sm', 'text-muted-foreground');
      });
    });
  });

  describe('DialogFooter', () => {
    it('renders footer content', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <DialogFooter>
              <button>Cancel</button>
              <button>Save</button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
      });
    });

    it('applies correct styling', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent>
            <DialogFooter data-testid="dialog-footer">Footer</DialogFooter>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const footer = screen.getByTestId('dialog-footer');
        expect(footer).toHaveClass(
          'flex',
          'flex-col-reverse',
          'sm:flex-row',
          'sm:justify-end',
          'sm:space-x-2'
        );
      });
    });
  });

  describe('Complete Dialog composition', () => {
    it('renders full dialog with all components', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Full Dialog</button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Complete Dialog</DialogTitle>
              <DialogDescription>
                This dialog has all components
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <p>Main dialog content</p>
            </div>
            <DialogFooter>
              <button>Cancel</button>
              <button>Confirm</button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open full dialog/i }));

      await waitFor(() => {
        expect(screen.getByText('Complete Dialog')).toBeInTheDocument();
        expect(screen.getByText('This dialog has all components')).toBeInTheDocument();
        expect(screen.getByText('Main dialog content')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument();
      });
    });

    it('maintains proper component hierarchy', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open</button>
          </DialogTrigger>
          <DialogContent data-testid="dialog-content">
            <DialogHeader data-testid="dialog-header">
              <DialogTitle data-testid="dialog-title">Title</DialogTitle>
            </DialogHeader>
            <div data-testid="dialog-body">Body</div>
            <DialogFooter data-testid="dialog-footer">Footer</DialogFooter>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open/i }));

      await waitFor(() => {
        const content = screen.getByTestId('dialog-content');
        const header = screen.getByTestId('dialog-header');
        const title = screen.getByTestId('dialog-title');
        const body = screen.getByTestId('dialog-body');
        const footer = screen.getByTestId('dialog-footer');

        expect(content).toContainElement(header);
        expect(header).toContainElement(title);
        expect(content).toContainElement(body);
        expect(content).toContainElement(footer);
      });
    });
  });

  describe('Accessibility', () => {
    it('supports ARIA attributes', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Accessible Dialog</button>
          </DialogTrigger>
          <DialogContent
            aria-labelledby="dialog-title"
            aria-describedby="dialog-description"
          >
            <DialogHeader>
              <DialogTitle id="dialog-title">Accessible Dialog</DialogTitle>
              <DialogDescription id="dialog-description">
                This dialog follows accessibility guidelines
              </DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
      );

      await user.click(screen.getByRole('button', { name: /open accessible dialog/i }));

      await waitFor(() => {
        const dialog = screen.getByRole('dialog', { name: /accessible dialog/i });
        expect(dialog).toBeInTheDocument();
        expect(dialog).toHaveAttribute('aria-modal', 'true');
        expect(dialog).toHaveAttribute('aria-labelledby', 'dialog-title');
        expect(dialog).toHaveAttribute('aria-describedby', 'dialog-description');
      });
    });

    it('restores focus to trigger after closing', async () => {
      const user = userEvent.setup();

      render(
        <Dialog>
          <DialogTrigger asChild>
            <button>Open Dialog</button>
          </DialogTrigger>
          <DialogContent>
            <p>Content</p>
            <button onClick={() => {}}>Inside Dialog</button>
          </DialogContent>
        </Dialog>
      );

      const trigger = screen.getByRole('button', { name: /open dialog/i });
      await user.click(trigger);

      await waitFor(() => {
        expect(screen.getByText('Content')).toBeInTheDocument();
      });

      await user.keyboard('{Escape}');

      await waitFor(() => {
        expect(trigger).toHaveFocus();
      });
    });
  });
});
