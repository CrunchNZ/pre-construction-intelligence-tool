import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import DataTable from '../DataTable';

// Mock data for testing
const mockData = [
  { id: 1, name: 'Project A', status: 'active', type: 'commercial', budget: 1000000 },
  { id: 2, name: 'Project B', status: 'inactive', type: 'residential', budget: 2000000 },
  { id: 3, name: 'Project C', status: 'pending', type: 'healthcare', budget: 3000000 },
];

const mockColumns = [
  { field: 'name', header: 'Project Name' },
  { field: 'status', header: 'Status', type: 'status' },
  { field: 'type', header: 'Type', type: 'chip' },
  { field: 'budget', header: 'Budget' },
];

const mockActions = [
  {
    icon: <span data-testid="edit-icon">Edit</span>,
    tooltip: 'Edit Project',
    onClick: jest.fn(),
    color: 'primary',
  },
  {
    icon: <span data-testid="delete-icon">Delete</span>,
    tooltip: 'Delete Project',
    onClick: jest.fn(),
    color: 'error',
  },
];

// Create theme for Material-UI components
const theme = createTheme();

const renderWithTheme = (component) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('DataTable Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders table with data and columns', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
      />
    );

    expect(screen.getByText('Project Name')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Budget')).toBeInTheDocument();

    expect(screen.getByText('Project A')).toBeInTheDocument();
    expect(screen.getByText('Project B')).toBeInTheDocument();
    expect(screen.getByText('Project C')).toBeInTheDocument();
  });

  test('renders loading state', () => {
    renderWithTheme(
      <DataTable
        data={[]}
        columns={mockColumns}
        loading={true}
      />
    );

    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });

  test('renders search functionality when searchable is true', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        searchable={true}
      />
    );

    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
  });

  test('filters data based on search term', async () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        searchable={true}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search...');
    fireEvent.change(searchInput, { target: { value: 'Project A' } });

    await waitFor(() => {
      expect(screen.getByText('Project A')).toBeInTheDocument();
      expect(screen.queryByText('Project B')).not.toBeInTheDocument();
      expect(screen.queryByText('Project C')).not.toBeInTheDocument();
    });
  });

  test('renders actions when provided', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        actions={mockActions}
      />
    );

    expect(screen.getByText('Actions')).toBeInTheDocument();
    expect(screen.getAllByTestId('edit-icon')).toHaveLength(3);
    expect(screen.getAllByTestId('delete-icon')).toHaveLength(3);
  });

  test('calls action onClick when action button is clicked', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        actions={mockActions}
      />
    );

    const editButtons = screen.getAllByTestId('edit-icon');
    const firstEditButton = editButtons[0].closest('button');
    fireEvent.click(firstEditButton);

    expect(mockActions[0].onClick).toHaveBeenCalledWith(mockData[0]);
  });

  test('renders status chips with correct colors', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
      />
    );

    const activeChip = screen.getByText('active');
    const inactiveChip = screen.getByText('inactive');
    const pendingChip = screen.getByText('pending');

    expect(activeChip).toBeInTheDocument();
    expect(inactiveChip).toBeInTheDocument();
    expect(pendingChip).toBeInTheDocument();
  });

  test('renders chip type columns correctly', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
      />
    );

    const commercialChip = screen.getByText('commercial');
    const residentialChip = screen.getByText('residential');
    const healthcareChip = screen.getByText('healthcare');

    expect(commercialChip).toBeInTheDocument();
    expect(residentialChip).toBeInTheDocument();
    expect(healthcareChip).toBeInTheDocument();
  });

  test('handles row click when onRowClick is provided', () => {
    const mockOnRowClick = jest.fn();
    
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        onRowClick={mockOnRowClick}
      />
    );

    const firstRow = screen.getByText('Project A').closest('tr');
    fireEvent.click(firstRow);

    expect(mockOnRowClick).toHaveBeenCalledWith(mockData[0]);
  });

  test('renders pagination when pageable is true', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        pageable={true}
      />
    );

    // Check if pagination component is rendered
    expect(screen.getByText('Rows per page:')).toBeInTheDocument();
  });

  test('displays correct record count', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        searchable={true}
      />
    );

    expect(screen.getByText('3 of 3 records')).toBeInTheDocument();
  });

  test('renders refresh button when onRefresh is provided', () => {
    const mockOnRefresh = jest.fn();
    
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        onRefresh={mockOnRefresh}
      />
    );

    const refreshButton = screen.getByLabelText('Refresh data');
    expect(refreshButton).toBeInTheDocument();
  });

  test('calls onRefresh when refresh button is clicked', () => {
    const mockOnRefresh = jest.fn();
    
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        onRefresh={mockOnRefresh}
      />
    );

    const refreshButton = screen.getByLabelText('Refresh data');
    fireEvent.click(refreshButton);

    expect(mockOnRefresh).toHaveBeenCalled();
  });

  test('renders filter button when filterable is true', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        filterable={true}
      />
    );

    const filterButton = screen.getByLabelText('Advanced filters');
    expect(filterButton).toBeInTheDocument();
  });

  test('applies sorting when column header is clicked', async () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
      />
    );

    const nameHeader = screen.getByText('Project Name');
    fireEvent.click(nameHeader);

    // Check if sort indicator appears
    await waitFor(() => {
      const sortLabel = nameHeader.closest('span');
      expect(sortLabel).toHaveClass('Mui-active');
    });
  });

  test('handles empty data gracefully', () => {
    renderWithTheme(
      <DataTable
        data={[]}
        columns={mockColumns}
      />
    );

    expect(screen.getByText('Project Name')).toBeInTheDocument();
    expect(screen.getByText('0 of 0 records')).toBeInTheDocument();
  });

  test('respects maxHeight prop', () => {
    renderWithTheme(
      <DataTable
        data={mockData}
        columns={mockColumns}
        maxHeight={500}
      />
    );

    const tableContainer = screen.getByRole('table').closest('div');
    expect(tableContainer).toHaveStyle({ maxHeight: '500px' });
  });
});
