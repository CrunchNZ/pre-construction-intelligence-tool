import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import Integrations from './Integrations.jsx';

describe('Integrations Component', () => {
  test('can be imported and rendered', () => {
    expect(Integrations).toBeDefined();
    expect(typeof Integrations).toBe('function');
    
    render(<Integrations />);
    expect(screen.getByText('Integrations')).toBeInTheDocument();
  });

  test('loads integrations after loading', async () => {
    render(<Integrations />);
    
    await waitFor(() => {
      expect(screen.getByText('Procore')).toBeInTheDocument();
    }, { timeout: 5000 });
    
    expect(screen.getByText('Jobpac')).toBeInTheDocument();
    expect(screen.getByText('Greentree')).toBeInTheDocument();
  });

  test('displays summary cards', async () => {
    render(<Integrations />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Integrations')).toBeInTheDocument();
      expect(screen.getByText('Connected')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('displays integration details correctly', async () => {
    render(<Integrations />);
    
    await waitFor(() => {
      expect(screen.getByText('Procore')).toBeInTheDocument();
    }, { timeout: 5000 });
    
    // Check that integration details are displayed
    expect(screen.getByText('Leading construction project management platform')).toBeInTheDocument();
    expect(screen.getByText('Construction Management')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument(); // Projects synced
  });
});
