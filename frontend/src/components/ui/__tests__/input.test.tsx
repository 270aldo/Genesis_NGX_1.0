import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '../input';

describe('Input Component', () => {
  it('renders input element', () => {
    render(<Input />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('renders with default type text', () => {
    render(<Input />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('type', 'text');
  });

  it('renders with custom type', () => {
    render(<Input type="email" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('type', 'email');
  });

  it('applies custom className', () => {
    render(<Input className="custom-input-class" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('custom-input-class');
    // Also check it maintains the default classes
    expect(input).toHaveClass('flex', 'h-10', 'w-full', 'rounded-md');
  });

  it('handles value changes', async () => {
    const user = userEvent.setup();
    render(<Input />);
    const input = screen.getByRole('textbox');
    
    await user.type(input, 'Hello World');
    expect(input).toHaveValue('Hello World');
  });

  it('handles onChange events', async () => {
    const handleChange = jest.fn();
    const user = userEvent.setup();
    
    render(<Input onChange={handleChange} />);
    const input = screen.getByRole('textbox');
    
    await user.type(input, 'Test');
    expect(handleChange).toHaveBeenCalled();
  });

  it('can be disabled', () => {
    render(<Input disabled />);
    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50');
  });

  it('shows placeholder text', () => {
    render(<Input placeholder="Enter your name" />);
    const input = screen.getByPlaceholderText('Enter your name');
    expect(input).toBeInTheDocument();
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it('handles focus and blur events', () => {
    const handleFocus = jest.fn();
    const handleBlur = jest.fn();
    
    render(<Input onFocus={handleFocus} onBlur={handleBlur} />);
    const input = screen.getByRole('textbox');
    
    fireEvent.focus(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);
    
    fireEvent.blur(input);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('supports different input types', () => {
    const types = ['password', 'email', 'number', 'tel', 'url', 'search'];
    
    types.forEach(type => {
      const { unmount } = render(<Input type={type} />);
      const input = screen.getByRole(type === 'search' ? 'searchbox' : 'textbox');
      expect(input).toHaveAttribute('type', type);
      unmount();
    });
  });

  it('applies correct focus styles', () => {
    render(<Input />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass(
      'focus-visible:outline-none',
      'focus-visible:ring-2',
      'focus-visible:ring-ring',
      'focus-visible:ring-offset-2'
    );
  });

  it('supports readOnly property', () => {
    render(<Input readOnly value="Read only text" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('readOnly');
    expect(input).toHaveValue('Read only text');
  });

  it('supports autoComplete attribute', () => {
    render(<Input autoComplete="email" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('autoComplete', 'email');
  });

  it('supports pattern validation', () => {
    render(<Input pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('pattern', '[0-9]{3}-[0-9]{3}-[0-9]{4}');
  });

  it('supports min and max for number inputs', () => {
    render(<Input type="number" min={0} max={100} />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('min', '0');
    expect(input).toHaveAttribute('max', '100');
  });

  it('handles file input styling', () => {
    render(<Input type="file" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass(
      'file:border-0',
      'file:bg-transparent',
      'file:text-sm',
      'file:font-medium'
    );
  });

  it('supports required attribute', () => {
    render(<Input required />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('required');
  });

  it('handles keyboard events', async () => {
    const handleKeyDown = jest.fn();
    const user = userEvent.setup();
    
    render(<Input onKeyDown={handleKeyDown} />);
    const input = screen.getByRole('textbox');
    
    await user.type(input, '{enter}');
    expect(handleKeyDown).toHaveBeenCalled();
  });

  it('maintains responsive text size', () => {
    render(<Input />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('text-base', 'md:text-sm');
  });
});