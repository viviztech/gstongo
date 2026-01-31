import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import LoadingSpinner from './LoadingSpinner';

describe('LoadingSpinner', () => {
    it('renders correctly', () => {
        const { container } = render(<LoadingSpinner />);
        const spinner = container.firstChild?.firstChild;
        expect(spinner).toHaveClass('animate-spin');
        expect(spinner).toHaveClass('w-8 h-8'); // default is md
    });

    it('renders with custom size', () => {
        const { container } = render(<LoadingSpinner size="lg" />);
        const spinner = container.firstChild?.firstChild;
        expect(spinner).toHaveClass('w-12 h-12');
    });

    it('renders with custom class', () => {
        const { container } = render(<LoadingSpinner className="mt-4" />);
        expect(container.firstChild).toHaveClass('mt-4');
    });
});
