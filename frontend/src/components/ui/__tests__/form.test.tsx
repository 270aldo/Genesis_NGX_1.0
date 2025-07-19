import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../form';
import { Input } from '../input';
import { Button } from '../button';

// Test form schema
const formSchema = z.object({
  username: z.string().min(2, {
    message: 'Username must be at least 2 characters.',
  }),
  email: z.string().email({
    message: 'Please enter a valid email address.',
  }),
  age: z.number().min(18, {
    message: 'You must be at least 18 years old.',
  }),
});

type FormData = z.infer<typeof formSchema>;

// Test component
function TestForm({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      email: '',
      age: 0,
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="Enter username" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="email@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="age"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Age</FormLabel>
              <FormControl>
                <Input 
                  type="number" 
                  placeholder="18" 
                  {...field}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}

describe('Form Components', () => {
  describe('Basic Form functionality', () => {
    it('renders form with all fields', () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      expect(screen.getByLabelText('Username')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Age')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
    });

    it('displays form descriptions', () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      expect(screen.getByText('This is your public display name.')).toBeInTheDocument();
    });

    it('submits form with valid data', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.type(screen.getByLabelText('Username'), 'johndoe');
      await user.type(screen.getByLabelText('Email'), 'john@example.com');
      await user.clear(screen.getByLabelText('Age'));
      await user.type(screen.getByLabelText('Age'), '25');
      
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(handleSubmit).toHaveBeenCalledWith({
          username: 'johndoe',
          email: 'john@example.com',
          age: 25,
        });
      });
    });
  });

  describe('Form validation', () => {
    it('shows validation errors for empty required fields', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Username must be at least 2 characters.')).toBeInTheDocument();
        expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
        expect(screen.getByText('You must be at least 18 years old.')).toBeInTheDocument();
      });

      expect(handleSubmit).not.toHaveBeenCalled();
    });

    it('shows validation error for short username', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.type(screen.getByLabelText('Username'), 'a');
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Username must be at least 2 characters.')).toBeInTheDocument();
      });
    });

    it('shows validation error for invalid email', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.type(screen.getByLabelText('Email'), 'not-an-email');
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
      });
    });

    it('shows validation error for underage user', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.type(screen.getByLabelText('Age'), '17');
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('You must be at least 18 years old.')).toBeInTheDocument();
      });
    });

    it('clears validation errors when corrected', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      // Submit with invalid data
      await user.type(screen.getByLabelText('Username'), 'a');
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Username must be at least 2 characters.')).toBeInTheDocument();
      });

      // Correct the error
      await user.clear(screen.getByLabelText('Username'));
      await user.type(screen.getByLabelText('Username'), 'johndoe');
      
      await waitFor(() => {
        expect(screen.queryByText('Username must be at least 2 characters.')).not.toBeInTheDocument();
      });
    });
  });

  describe('FormField component', () => {
    it('passes field props correctly to input', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      const usernameInput = screen.getByLabelText('Username');
      await user.type(usernameInput, 'testuser');

      expect(usernameInput).toHaveValue('testuser');
    });

    it('maintains form state between re-renders', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      const { rerender } = render(<TestForm onSubmit={handleSubmit} />);

      await user.type(screen.getByLabelText('Username'), 'testuser');
      
      rerender(<TestForm onSubmit={handleSubmit} />);

      expect(screen.getByLabelText('Username')).toHaveValue('testuser');
    });
  });

  describe('FormLabel component', () => {
    it('associates label with form control', () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      const usernameLabel = screen.getByText('Username');
      const usernameInput = screen.getByLabelText('Username');

      expect(usernameLabel).toHaveAttribute('for', usernameInput.id);
    });

    it('applies error styling when field has error', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        const usernameLabel = screen.getByText('Username');
        expect(usernameLabel).toHaveClass('text-destructive');
      });
    });
  });

  describe('FormControl component', () => {
    it('sets aria-invalid when field has error', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        const usernameInput = screen.getByLabelText('Username');
        expect(usernameInput).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('sets aria-describedby for accessibility', async () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      const usernameInput = screen.getByLabelText('Username');
      const describedBy = usernameInput.getAttribute('aria-describedby');
      
      expect(describedBy).toBeTruthy();
      expect(describedBy).toContain('description');
    });
  });

  describe('FormMessage component', () => {
    it('displays field-specific error messages', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.type(screen.getByLabelText('Username'), 'a');
      await user.type(screen.getByLabelText('Email'), 'invalid');
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Username must be at least 2 characters.')).toBeInTheDocument();
        expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();
      });
    });

    it('does not render when no error exists', () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      const errorMessages = screen.queryAllByText(/must be at least/);
      expect(errorMessages).toHaveLength(0);
    });

    it('applies error message styling', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        const errorMessage = screen.getByText('Username must be at least 2 characters.');
        expect(errorMessage).toHaveClass('text-sm', 'font-medium', 'text-destructive');
      });
    });
  });

  describe('FormDescription component', () => {
    it('renders helper text', () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      const description = screen.getByText('This is your public display name.');
      expect(description).toBeInTheDocument();
      expect(description).toHaveClass('text-sm', 'text-muted-foreground');
    });

    it('has correct id for aria-describedby', () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      const description = screen.getByText('This is your public display name.');
      expect(description).toHaveAttribute('id');
      
      const usernameInput = screen.getByLabelText('Username');
      const describedBy = usernameInput.getAttribute('aria-describedby');
      expect(describedBy).toContain(description.id);
    });
  });

  describe('Complex form scenarios', () => {
    it('handles multiple validation errors per field', async () => {
      const complexSchema = z.object({
        password: z.string()
          .min(8, 'Password must be at least 8 characters')
          .regex(/[A-Z]/, 'Password must contain uppercase letter')
          .regex(/[0-9]/, 'Password must contain number'),
      });

      function ComplexForm({ onSubmit }: { onSubmit: (data: any) => void }) {
        const form = useForm({
          resolver: zodResolver(complexSchema),
          defaultValues: { password: '' },
        });

        return (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit">Submit</Button>
            </form>
          </Form>
        );
      }

      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<ComplexForm onSubmit={handleSubmit} />);

      await user.type(screen.getByLabelText('Password'), 'short');
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        // Should show the first validation error
        expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();
      });
    });

    it('supports custom form controls', () => {
      function CustomForm({ onSubmit }: { onSubmit: (data: any) => void }) {
        const form = useForm({
          defaultValues: { terms: false },
        });

        return (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <FormField
                control={form.control}
                name="terms"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <label>
                        <input
                          type="checkbox"
                          checked={field.value}
                          onChange={field.onChange}
                        />
                        Accept terms
                      </label>
                    </FormControl>
                  </FormItem>
                )}
              />
              <Button type="submit">Submit</Button>
            </form>
          </Form>
        );
      }

      const handleSubmit = jest.fn();
      render(<CustomForm onSubmit={handleSubmit} />);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).not.toBeChecked();
    });
  });

  describe('Accessibility', () => {
    it('provides proper ARIA relationships', () => {
      const handleSubmit = jest.fn();
      render(<TestForm onSubmit={handleSubmit} />);

      const usernameInput = screen.getByLabelText('Username');
      const describedBy = usernameInput.getAttribute('aria-describedby');

      expect(describedBy).toBeTruthy();
      expect(describedBy?.split(' ')).toHaveLength(2); // description and message IDs
    });

    it('focuses first error field on submission', async () => {
      const handleSubmit = jest.fn();
      const user = userEvent.setup();
      
      render(<TestForm onSubmit={handleSubmit} />);

      // Submit empty form
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        // First field with error should receive focus
        expect(screen.getByLabelText('Username')).toHaveFocus();
      });
    });
  });
});