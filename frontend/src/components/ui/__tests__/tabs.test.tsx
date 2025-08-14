import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../tabs';

describe('Tabs Component', () => {
  describe('Tabs', () => {
    it('renders tabs container', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
        </Tabs>
      );

      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: 'Tab 1' })).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <Tabs defaultValue="tab1" className="custom-tabs">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
        </Tabs>
      );

      const tabsContainer = screen.getByRole('tablist').parentElement;
      expect(tabsContainer).toHaveClass('custom-tabs');
    });

    it('supports controlled state', async () => {
      const TestComponent = () => {
        const [value, setValue] = React.useState('tab1');

        return (
          <div>
            <button onClick={() => setValue('tab2')}>Switch to Tab 2</button>
            <Tabs value={value} onValueChange={setValue}>
              <TabsList>
                <TabsTrigger value="tab1">Tab 1</TabsTrigger>
                <TabsTrigger value="tab2">Tab 2</TabsTrigger>
              </TabsList>
              <TabsContent value="tab1">Content 1</TabsContent>
              <TabsContent value="tab2">Content 2</TabsContent>
            </Tabs>
          </div>
        );
      };

      const user = userEvent.setup();
      render(<TestComponent />);

      expect(screen.getByText('Content 1')).toBeInTheDocument();
      expect(screen.queryByText('Content 2')).not.toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: 'Switch to Tab 2' }));

      await waitFor(() => {
        expect(screen.getByText('Content 2')).toBeInTheDocument();
        expect(screen.queryByText('Content 1')).not.toBeInTheDocument();
      });
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(
        <Tabs ref={ref} defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
        </Tabs>
      );

      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('TabsList', () => {
    it('renders with correct role and styling', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList data-testid="tabs-list">
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
        </Tabs>
      );

      const tabsList = screen.getByTestId('tabs-list');
      expect(tabsList).toHaveAttribute('role', 'tablist');
      expect(tabsList).toHaveClass(
        'inline-flex',
        'h-10',
        'items-center',
        'justify-center',
        'rounded-md',
        'bg-muted',
        'p-1',
        'text-muted-foreground'
      );
    });

    it('applies custom className', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList className="custom-tabs-list">
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
        </Tabs>
      );

      const tabsList = screen.getByRole('tablist');
      expect(tabsList).toHaveClass('custom-tabs-list');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(
        <Tabs defaultValue="tab1">
          <TabsList ref={ref}>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
        </Tabs>
      );

      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('TabsTrigger', () => {
    it('renders with correct role and attributes', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      );

      const tab1 = screen.getByRole('tab', { name: 'Tab 1' });
      const tab2 = screen.getByRole('tab', { name: 'Tab 2' });

      expect(tab1).toHaveAttribute('data-state', 'active');
      expect(tab1).toHaveAttribute('aria-selected', 'true');
      expect(tab2).toHaveAttribute('data-state', 'inactive');
      expect(tab2).toHaveAttribute('aria-selected', 'false');
    });

    it('applies correct styling', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Active Tab</TabsTrigger>
            <TabsTrigger value="tab2">Inactive Tab</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      );

      const activeTab = screen.getByRole('tab', { name: 'Active Tab' });
      const inactiveTab = screen.getByRole('tab', { name: 'Inactive Tab' });

      expect(activeTab).toHaveClass(
        'inline-flex',
        'items-center',
        'justify-center',
        'whitespace-nowrap',
        'rounded-sm',
        'px-3',
        'py-1.5',
        'text-sm',
        'font-medium',
        'ring-offset-background',
        'transition-all',
        'focus-visible:outline-none',
        'focus-visible:ring-2',
        'focus-visible:ring-ring',
        'focus-visible:ring-offset-2',
        'disabled:pointer-events-none',
        'disabled:opacity-50',
        'data-[state=active]:bg-background',
        'data-[state=active]:text-foreground',
        'data-[state=active]:shadow-sm'
      );
    });

    it('switches tabs when clicked', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      );

      expect(screen.getByText('Content 1')).toBeInTheDocument();
      expect(screen.queryByText('Content 2')).not.toBeInTheDocument();

      await user.click(screen.getByRole('tab', { name: 'Tab 2' }));

      await waitFor(() => {
        expect(screen.getByText('Content 2')).toBeInTheDocument();
        expect(screen.queryByText('Content 1')).not.toBeInTheDocument();
      });
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
            <TabsTrigger value="tab3">Tab 3</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
          <TabsContent value="tab3">Content 3</TabsContent>
        </Tabs>
      );

      const tab1 = screen.getByRole('tab', { name: 'Tab 1' });
      const tab2 = screen.getByRole('tab', { name: 'Tab 2' });

      // Focus first tab
      tab1.focus();
      expect(tab1).toHaveFocus();

      // Arrow right to second tab
      await user.keyboard('{ArrowRight}');
      expect(tab2).toHaveFocus();

      // Space or Enter should activate the focused tab
      await user.keyboard(' ');

      await waitFor(() => {
        expect(screen.getByText('Content 2')).toBeInTheDocument();
      });
    });

    it('can be disabled', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2" disabled>Disabled Tab</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      );

      const disabledTab = screen.getByRole('tab', { name: 'Disabled Tab' });
      expect(disabledTab).toBeDisabled();
      expect(disabledTab).toHaveClass('disabled:pointer-events-none', 'disabled:opacity-50');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLButtonElement>();
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger ref={ref} value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
        </Tabs>
      );

      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    });
  });

  describe('TabsContent', () => {
    it('renders content for active tab', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Active content</TabsContent>
          <TabsContent value="tab2">Inactive content</TabsContent>
        </Tabs>
      );

      expect(screen.getByText('Active content')).toBeInTheDocument();
      expect(screen.queryByText('Inactive content')).not.toBeInTheDocument();
    });

    it('applies correct role and attributes', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" data-testid="tab-content">
            Content 1
          </TabsContent>
        </Tabs>
      );

      const content = screen.getByTestId('tab-content');
      expect(content).toHaveAttribute('role', 'tabpanel');
      expect(content).toHaveAttribute('data-state', 'active');
    });

    it('applies correct styling', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" data-testid="tab-content">
            Content 1
          </TabsContent>
        </Tabs>
      );

      const content = screen.getByTestId('tab-content');
      expect(content).toHaveClass(
        'mt-2',
        'ring-offset-background',
        'focus-visible:outline-none',
        'focus-visible:ring-2',
        'focus-visible:ring-ring',
        'focus-visible:ring-offset-2'
      );
    });

    it('can be focused', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" tabIndex={0}>
            Focusable content
          </TabsContent>
        </Tabs>
      );

      const content = screen.getByText('Focusable content');
      content.focus();
      expect(content).toHaveFocus();
    });

    it('applies custom className', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" className="custom-content">
            Content 1
          </TabsContent>
        </Tabs>
      );

      const content = screen.getByText('Content 1');
      expect(content).toHaveClass('custom-content');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent ref={ref} value="tab1">
            Content 1
          </TabsContent>
        </Tabs>
      );

      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('Complete Tabs composition', () => {
    it('renders multiple tabs with proper switching', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="overview">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
          </TabsList>
          <TabsContent value="overview">Overview content</TabsContent>
          <TabsContent value="analytics">Analytics content</TabsContent>
          <TabsContent value="reports">Reports content</TabsContent>
          <TabsContent value="notifications">Notifications content</TabsContent>
        </Tabs>
      );

      // Initial state
      expect(screen.getByText('Overview content')).toBeInTheDocument();

      // Switch to analytics
      await user.click(screen.getByRole('tab', { name: 'Analytics' }));
      await waitFor(() => {
        expect(screen.getByText('Analytics content')).toBeInTheDocument();
        expect(screen.queryByText('Overview content')).not.toBeInTheDocument();
      });

      // Switch to reports
      await user.click(screen.getByRole('tab', { name: 'Reports' }));
      await waitFor(() => {
        expect(screen.getByText('Reports content')).toBeInTheDocument();
        expect(screen.queryByText('Analytics content')).not.toBeInTheDocument();
      });
    });

    it('maintains proper ARIA relationships', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList aria-label="Main navigation">
            <TabsTrigger value="tab1">First Tab</TabsTrigger>
            <TabsTrigger value="tab2">Second Tab</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">First content</TabsContent>
          <TabsContent value="tab2">Second content</TabsContent>
        </Tabs>
      );

      const tabList = screen.getByRole('tablist');
      const activeTab = screen.getByRole('tab', { selected: true });
      const activeContent = screen.getByRole('tabpanel');

      expect(tabList).toHaveAttribute('aria-label', 'Main navigation');
      expect(activeTab).toHaveAttribute('aria-selected', 'true');
      expect(activeContent).toBeInTheDocument();
    });

    it('supports complex content in tabs', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="form">
          <TabsList>
            <TabsTrigger value="form">Form</TabsTrigger>
            <TabsTrigger value="table">Table</TabsTrigger>
          </TabsList>
          <TabsContent value="form">
            <form>
              <input type="text" placeholder="Name" />
              <button type="submit">Submit</button>
            </form>
          </TabsContent>
          <TabsContent value="table">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Age</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>John</td>
                  <td>25</td>
                </tr>
              </tbody>
            </table>
          </TabsContent>
        </Tabs>
      );

      // Form tab content
      expect(screen.getByPlaceholderText('Name')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();

      // Switch to table tab
      await user.click(screen.getByRole('tab', { name: 'Table' }));

      await waitFor(() => {
        expect(screen.getByRole('table')).toBeInTheDocument();
        expect(screen.getByText('John')).toBeInTheDocument();
        expect(screen.queryByPlaceholderText('Name')).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('supports full keyboard navigation', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
            <TabsTrigger value="tab3">Tab 3</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
          <TabsContent value="tab3">Content 3</TabsContent>
        </Tabs>
      );

      const tab1 = screen.getByRole('tab', { name: 'Tab 1' });
      const tab2 = screen.getByRole('tab', { name: 'Tab 2' });
      const tab3 = screen.getByRole('tab', { name: 'Tab 3' });

      // Tab to first tab
      await user.tab();
      expect(tab1).toHaveFocus();

      // Arrow navigation
      await user.keyboard('{ArrowRight}');
      expect(tab2).toHaveFocus();

      await user.keyboard('{ArrowRight}');
      expect(tab3).toHaveFocus();

      // Wrap around to first tab
      await user.keyboard('{ArrowRight}');
      expect(tab1).toHaveFocus();

      // Arrow left navigation
      await user.keyboard('{ArrowLeft}');
      expect(tab3).toHaveFocus();
    });

    it('supports Home and End keys', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="tab2">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
            <TabsTrigger value="tab3">Tab 3</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
          <TabsContent value="tab3">Content 3</TabsContent>
        </Tabs>
      );

      const tab1 = screen.getByRole('tab', { name: 'Tab 1' });
      const tab2 = screen.getByRole('tab', { name: 'Tab 2' });
      const tab3 = screen.getByRole('tab', { name: 'Tab 3' });

      // Focus middle tab
      tab2.focus();
      expect(tab2).toHaveFocus();

      // Home should go to first tab
      await user.keyboard('{Home}');
      expect(tab1).toHaveFocus();

      // End should go to last tab
      await user.keyboard('{End}');
      expect(tab3).toHaveFocus();
    });

    it('properly associates tabs with their content', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">First</TabsTrigger>
            <TabsTrigger value="tab2">Second</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">First panel</TabsContent>
          <TabsContent value="tab2">Second panel</TabsContent>
        </Tabs>
      );

      const activeTab = screen.getByRole('tab', { selected: true });
      const activePanel = screen.getByRole('tabpanel');

      expect(activeTab).toHaveAttribute('aria-controls');
      expect(activePanel).toHaveAttribute('aria-labelledby');
    });

    it('announces tab changes to screen readers', async () => {
      const user = userEvent.setup();

      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Announcements</TabsTrigger>
            <TabsTrigger value="tab2">Messages</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" aria-live="polite">
            Announcements content
          </TabsContent>
          <TabsContent value="tab2" aria-live="polite">
            Messages content
          </TabsContent>
        </Tabs>
      );

      await user.click(screen.getByRole('tab', { name: 'Messages' }));

      await waitFor(() => {
        const activePanel = screen.getByRole('tabpanel');
        expect(activePanel).toHaveAttribute('aria-live', 'polite');
      });
    });
  });

  describe('Edge cases', () => {
    it('handles tabs without content gracefully', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Only first tab has content</TabsContent>
        </Tabs>
      );

      expect(screen.getByText('Only first tab has content')).toBeInTheDocument();
      // Second tab exists but has no content panel
      expect(screen.getByRole('tab', { name: 'Tab 2' })).toBeInTheDocument();
    });

    it('handles invalid default value', () => {
      render(
        <Tabs defaultValue="nonexistent">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      );

      // Should still render without crashing
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: 'Tab 1' })).toBeInTheDocument();
    });

    it('handles single tab scenario', () => {
      render(
        <Tabs defaultValue="only-tab">
          <TabsList>
            <TabsTrigger value="only-tab">Only Tab</TabsTrigger>
          </TabsList>
          <TabsContent value="only-tab">Only content</TabsContent>
        </Tabs>
      );

      expect(screen.getByRole('tab', { name: 'Only Tab' })).toBeInTheDocument();
      expect(screen.getByText('Only content')).toBeInTheDocument();
    });
  });
});
