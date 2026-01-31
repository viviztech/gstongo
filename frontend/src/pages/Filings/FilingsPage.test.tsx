import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import FilingsPage from './FilingsPage';
import * as apiModule from '../../services/api';

// Mock the API module
vi.mock('../../services/api', async (importOriginal) => {
    const actual = await importOriginal<typeof apiModule>();
    return {
        ...actual,
        gstFilingAPI: {
            getFilings: vi.fn(),
            createFiling: vi.fn(),
        },
    };
});

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
        },
    },
});

const renderWithProviders = (ui: React.ReactElement) => {
    return render(
        <QueryClientProvider client={queryClient}>
            <MemoryRouter>
                {ui}
            </MemoryRouter>
        </QueryClientProvider>
    );
};

describe('FilingsPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        queryClient.clear();
    });

    it('renders page title and create button', async () => {
        (apiModule.gstFilingAPI.getFilings as any).mockResolvedValue({ data: [] });

        renderWithProviders(<FilingsPage />);

        // Wait for loading to finish
        expect(await screen.findByText('GST Return Filings')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Create New Filing/i })).toBeInTheDocument();
    });

    it('displays filings list', async () => {
        const mockFilings = [
            {
                id: '1',
                filing_type: 'GSTR1',
                financial_year: '2024-25',
                month: 4,
                year: 2024,
                status: 'filed',
                nil_filing: false,
                created_at: '2024-05-01T10:00:00Z',
            },
            {
                id: '2',
                filing_type: 'GSTR3B',
                financial_year: '2024-25',
                month: 5,
                year: 2024,
                status: 'pending',
                nil_filing: true,
                created_at: '2024-05-02T10:00:00Z',
            }
        ];

        (apiModule.gstFilingAPI.getFilings as any).mockResolvedValue({ data: mockFilings });

        renderWithProviders(<FilingsPage />);

        // Wait for data to load
        expect(await screen.findByText('GSTR1')).toBeInTheDocument();

        expect(screen.getByText('GSTR3B')).toBeInTheDocument();
        expect(screen.getByText('April 2024')).toBeInTheDocument(); // 4 = April

        // Check Statuses by text can be tricky if "Filed" appears multiple times (stats + table)
        // Using getAllByText is safer
        expect(screen.getAllByText(/Filed/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/Pending/i).length).toBeGreaterThan(0);
    });

    it('opens create modal on button click', async () => {
        (apiModule.gstFilingAPI.getFilings as any).mockResolvedValue({ data: [] });

        renderWithProviders(<FilingsPage />);

        const createBtn = await screen.findByRole('button', { name: /Create New Filing/i });
        fireEvent.click(createBtn);

        // Check for modal header
        expect(await screen.findByRole('heading', { name: 'Create New Filing' })).toBeInTheDocument();
        // Check for form fields
        expect(screen.getByText('Filing Type')).toBeInTheDocument();
        expect(screen.getByText('Financial Year')).toBeInTheDocument();
    });
});
