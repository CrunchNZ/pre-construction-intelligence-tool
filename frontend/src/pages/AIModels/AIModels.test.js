import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AIModels from './AIModels';

// Mock fetch
global.fetch = jest.fn();

// Mock components
jest.mock('../../components/common/DataTable', () => {
  return function MockDataTable({ data, columns, loading }) {
    return (
      <div data-testid="data-table">
        {loading ? (
          <div>Loading...</div>
        ) : (
          <div>
            {data.map((item, index) => (
              <div key={index} data-testid={`table-row-${index}`}>
                {columns.map((col, colIndex) => (
                  <div key={colIndex} data-testid={`cell-${col.field}-${index}`}>
                    {col.renderCell ? col.renderCell({ value: item[col.field], row: item }) : item[col.field]}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };
});

jest.mock('../../components/common/Modal', () => {
  return function MockModal({ open, onClose, title, children, maxWidth }) {
    if (!open) return null;
    return (
      <div data-testid="modal">
        <h2>{title}</h2>
        {children}
        <button onClick={onClose}>Close</button>
      </div>
    );
  };
});

jest.mock('../../components/common/Notification', () => {
  return function MockNotification({ open, message, severity, onClose }) {
    if (!open) return null;
    return (
      <div data-testid="notification" data-severity={severity}>
        {message}
        <button onClick={onClose}>Close</button>
      </div>
    );
  };
});

jest.mock('../../components/common/Chart', () => {
  return function MockChart({ type, data, options }) {
    return (
      <div data-testid="chart" data-type={type}>
        Chart Component
      </div>
    );
  };
});

const theme = createTheme();

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

const mockModels = [
  {
    id: 1,
    name: 'Cost Prediction Model',
    model_type: 'cost_prediction',
    algorithm: 'Random Forest',
    status: 'active',
    accuracy: 0.85,
    last_trained: '2024-01-15T10:00:00Z',
    version: '1.0.0',
    description: 'Model for predicting construction costs',
    feature_columns: ['area', 'complexity', 'location'],
    target_column: 'cost',
    performance_summary: { accuracy: 0.85, precision: 0.82, recall: 0.88 }
  },
  {
    id: 2,
    name: 'Timeline Model',
    model_type: 'timeline_prediction',
    algorithm: 'Linear Regression',
    status: 'draft',
    accuracy: null,
    last_trained: null,
    version: '1.0.0',
    description: 'Model for predicting project timelines',
    feature_columns: ['scope', 'team_size'],
    target_column: 'timeline',
    performance_summary: {}
  }
];

describe('AIModels Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders AI Models page with title and create button', () => {
    renderWithProviders(<AIModels />);
    
    expect(screen.getByText('AI Models')).toBeInTheDocument();
    expect(screen.getByText('Create Model')).toBeInTheDocument();
  });

  test('renders tabs for different model views', () => {
    renderWithProviders(<AIModels />);
    
    expect(screen.getByText('All Models')).toBeInTheDocument();
    expect(screen.getByText('Active Models')).toBeInTheDocument();
    expect(screen.getByText('Training Models')).toBeInTheDocument();
    expect(screen.getByText('Performance')).toBeInTheDocument();
  });

  test('fetches models on component mount', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    renderWithProviders(<AIModels />);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/ai_models/models/');
    });
  });

  test('displays models in data table', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    renderWithProviders(<AIModels />);
    
    await waitFor(() => {
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
      expect(screen.getByTestId('table-row-0')).toBeInTheDocument();
      expect(screen.getByTestId('table-row-1')).toBeInTheDocument();
    });
  });

  test('opens create model modal when create button is clicked', () => {
    renderWithProviders(<AIModels />);
    
    fireEvent.click(screen.getByText('Create Model'));
    
    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByText('Create New AI Model')).toBeInTheDocument();
  });

  test('creates new model successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 3, name: 'New Model' })
    });

    renderWithProviders(<AIModels />);
    
    // Open create modal
    fireEvent.click(screen.getByText('Create Model'));
    
    // Fill form
    fireEvent.change(screen.getByLabelText('Model Name'), {
      target: { value: 'New Model' }
    });
    
    fireEvent.change(screen.getByLabelText('Model Type'), {
      target: { value: 'cost_prediction' }
    });
    
    fireEvent.change(screen.getByLabelText('Algorithm'), {
      target: { value: 'Random Forest' }
    });
    
    fireEvent.change(screen.getByLabelText('Feature Columns (comma-separated)'), {
      target: { value: 'area, complexity' }
    });
    
    fireEvent.change(screen.getByLabelText('Target Column'), {
      target: { value: 'cost' }
    });
    
    // Submit form
    fireEvent.click(screen.getByText('Create Model'));
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/ai_models/models/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'New Model',
          model_type: 'cost_prediction',
          version: '1.0.0',
          description: '',
          algorithm: 'Random Forest',
          hyperparameters: {},
          feature_columns: ['area', 'complexity'],
          target_column: 'cost'
        })
      });
    });
  });

  test('handles model creation error', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    fetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithProviders(<AIModels />);
    
    // Open create modal
    fireEvent.click(screen.getByText('Create Model'));
    
    // Fill form
    fireEvent.change(screen.getByLabelText('Model Name'), {
      target: { value: 'New Model' }
    });
    
    fireEvent.change(screen.getByLabelText('Model Type'), {
      target: { value: 'cost_prediction' }
    });
    
    fireEvent.change(screen.getByLabelText('Algorithm'), {
      target: { value: 'Random Forest' }
    });
    
    fireEvent.change(screen.getByLabelText('Feature Columns (comma-separated)'), {
      target: { value: 'area, complexity' }
    });
    
    fireEvent.change(screen.getByLabelText('Target Column'), {
      target: { value: 'cost' }
    });
    
    // Submit form
    fireEvent.click(screen.getByText('Create Model'));
    
    await waitFor(() => {
      expect(screen.getByTestId('notification')).toBeInTheDocument();
      expect(screen.getByText('Failed to create model')).toBeInTheDocument();
    });
  });

  test('trains model successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Training started' })
    });

    renderWithProviders(<AIModels />);
    
    await waitFor(() => {
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });
    
    // Find and click train button for draft model
    const trainButtons = screen.getAllByTestId(/cell-actions-\d+/);
    const draftModelTrainButton = trainButtons.find(button => 
      button.textContent.includes('Train Model')
    );
    
    if (draftModelTrainButton) {
      fireEvent.click(draftModelTrainButton);
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/ai_models/models/2/train/', {
          method: 'POST'
        });
      });
    }
  });

  test('deploys model successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Model deployed' })
    });

    renderWithProviders(<AIModels />);
    
    await waitFor(() => {
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });
    
    // Find and click deploy button for active model
    const actionCells = screen.getAllByTestId(/cell-actions-\d+/);
    const activeModelDeployButton = actionCells.find(button => 
      button.textContent.includes('Deploy Model')
    );
    
    if (activeModelDeployButton) {
      fireEvent.click(activeModelDeployButton);
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/ai_models/models/1/deploy/', {
          method: 'POST'
        });
      });
    }
  });

  test('deletes model with confirmation', async () => {
    global.confirm = jest.fn(() => true);
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Model deleted' })
    });

    renderWithProviders(<AIModels />);
    
    await waitFor(() => {
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });
    
    // Find and click delete button
    const actionCells = screen.getAllByTestId(/cell-actions-\d+/);
    const deleteButton = actionCells.find(button => 
      button.textContent.includes('Delete')
    );
    
    if (deleteButton) {
      fireEvent.click(deleteButton);
      
      expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this model?');
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/ai_models/models/1/', {
          method: 'DELETE'
        });
      });
    }
  });

  test('switches between tabs correctly', () => {
    renderWithProviders(<AIModels />);
    
    // Click on Performance tab
    fireEvent.click(screen.getByText('Performance'));
    
    expect(screen.getByText('Model Performance Overview')).toBeInTheDocument();
    expect(screen.getByText('Total Models')).toBeInTheDocument();
    expect(screen.getByText('Active Models')).toBeInTheDocument();
    expect(screen.getByText('Training Models')).toBeInTheDocument();
  });

  test('displays model performance metrics correctly', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    renderWithProviders(<AIModels />);
    
    await waitFor(() => {
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });
    
    // Click on Performance tab
    fireEvent.click(screen.getByText('Performance'));
    
    // Check performance overview cards
    expect(screen.getByText('Total Models')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Total models count
    
    expect(screen.getByText('Active Models')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument(); // Active models count
    
    expect(screen.getByText('Training Models')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument(); // Training models count
  });

  test('handles fetch error gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithProviders(<AIModels />);
    
    await waitFor(() => {
      expect(screen.getByTestId('notification')).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch models')).toBeInTheDocument();
    });
  });

  test('form validation works correctly', () => {
    renderWithProviders(<AIModels />);
    
    // Open create modal
    fireEvent.click(screen.getByText('Create Model'));
    
    // Try to submit without required fields
    fireEvent.click(screen.getByText('Create Model'));
    
    // Form should still be open (no submission)
    expect(screen.getByTestId('modal')).toBeInTheDocument();
  });

  test('resets form after successful creation', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockModels
    });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 3, name: 'New Model' })
    });

    renderWithProviders(<AIModels />);
    
    // Open create modal
    fireEvent.click(screen.getByText('Create Model'));
    
    // Fill form
    fireEvent.change(screen.getByLabelText('Model Name'), {
      target: { value: 'New Model' }
    });
    
    // Submit form
    fireEvent.click(screen.getByText('Create Model'));
    
    await waitFor(() => {
      // Modal should close
      expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
    });
    
    // Open modal again to check if form is reset
    fireEvent.click(screen.getByText('Create Model'));
    
    expect(screen.getByDisplayValue('')).toBeInTheDocument(); // Name field should be empty
  });
});
