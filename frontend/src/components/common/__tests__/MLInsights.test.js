import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import MLInsights from '../MLInsights';
import mlInsightsReducer from '../../../store/slices/mlInsightsSlice';

// Mock store setup
const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      mlInsights: mlInsightsReducer,
    },
    preloadedState: {
      mlInsights: {
        dashboardInsights: null,
        dashboardLoading: false,
        dashboardError: null,
        projectInsights: {},
        projectInsightsLoading: {},
        projectInsightsError: {},
        riskAnalysisInsights: null,
        riskAnalysisLoading: false,
        riskAnalysisError: null,
        reportsInsights: {},
        reportsInsightsLoading: {},
        reportsInsightsError: {},
        ...initialState,
      },
    },
  });
};

// Test wrapper component
const TestWrapper = ({ children, initialState = {} }) => {
  const store = createTestStore(initialState);
  return <Provider store={store}>{children}</Provider>;
};

describe('MLInsights Component', () => {
  const mockOnRefresh = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Dashboard Insights Type', () => {
    it('renders dashboard insights correctly', () => {
      const initialState = {
        dashboardInsights: {
          cost_predictions: {
            total_predicted_cost: 1500000,
            avg_prediction_confidence: 0.85,
            recent_predictions_count: 25,
            active_models_count: 3,
          },
          risk_insights: {
            high_risk_count: 5,
            total_risks: 15,
          },
          timeline_predictions: {
            avg_prediction_confidence: 0.78,
          },
          last_updated: '2024-01-15T10:30:00Z',
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights
            type="dashboard"
            title="AI-Powered Insights"
            showRefresh={true}
            onRefresh={mockOnRefresh}
          />
        </TestWrapper>
      );

      expect(screen.getByText('AI-Powered Insights')).toBeInTheDocument();
      expect(screen.getByText('$1,500,000')).toBeInTheDocument();
      expect(screen.getByText('Confidence: 85.0%')).toBeInTheDocument();
      expect(screen.getByText('5 High Risk')).toBeInTheDocument();
      expect(screen.getByText('Total: 15')).toBeInTheDocument();
      expect(screen.getByText('78.0%')).toBeInTheDocument();
    });

    it('shows loading state', () => {
      const initialState = {
        dashboardLoading: true,
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights type="dashboard" title="AI-Powered Insights" />
        </TestWrapper>
      );

      expect(screen.getByText('Loading AI insights...')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('shows error state', () => {
      const initialState = {
        dashboardError: 'Failed to fetch insights',
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights type="dashboard" title="AI-Powered Insights" />
        </TestWrapper>
      );

      expect(screen.getByText('Failed to fetch insights')).toBeInTheDocument();
      expect(screen.getByText('Unable to load AI insights. Please try refreshing.')).toBeInTheDocument();
    });

    it('shows no data state', () => {
      render(
        <TestWrapper>
          <MLInsights type="dashboard" title="AI-Powered Insights" />
        </TestWrapper>
      );

      expect(screen.getByText('No AI insights available at this time.')).toBeInTheDocument();
    });
  });

  describe('Project Insights Type', () => {
    it('renders project insights correctly', () => {
      const initialState = {
        projectInsights: {
          1: {
            project_id: 1,
            project_name: 'Test Project',
            cost_prediction: {
              predicted_cost: 500000,
              confidence: 0.92,
            },
            timeline_prediction: {
              predicted_duration: 180,
              confidence: 0.88,
            },
            risk_assessment: {
              risk_level: 'medium',
              description: 'Moderate risk due to weather conditions',
            },
            last_updated: '2024-01-15T10:30:00Z',
          },
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights
            type="project"
            projectId={1}
            title="Project AI Insights"
            showRefresh={true}
            onRefresh={mockOnRefresh}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Project AI Insights')).toBeInTheDocument();
      expect(screen.getByText('$500,000')).toBeInTheDocument();
      expect(screen.getByText('Confidence: 92.0%')).toBeInTheDocument();
      expect(screen.getByText('180 days')).toBeInTheDocument();
      expect(screen.getByText('Confidence: 88.0%')).toBeInTheDocument();
      expect(screen.getByText('medium')).toBeInTheDocument();
      expect(screen.getByText('Moderate risk due to weather conditions')).toBeInTheDocument();
    });
  });

  describe('Risk Analysis Insights Type', () => {
    it('renders risk analysis insights correctly', () => {
      const initialState = {
        riskAnalysisInsights: {
          overall_risk_score: 7.5,
          high_risk_projects: [
            { id: 1, name: 'High Risk Project 1' },
            { id: 2, name: 'High Risk Project 2' },
          ],
          last_updated: '2024-01-15T10:30:00Z',
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights
            type="risk"
            title="AI Risk Intelligence"
            showRefresh={true}
            onRefresh={mockOnRefresh}
          />
        </TestWrapper>
      );

      expect(screen.getByText('AI Risk Intelligence')).toBeInTheDocument();
      expect(screen.getByText('7.5/10')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('Require immediate attention')).toBeInTheDocument();
    });
  });

  describe('Reports Insights Type', () => {
    it('renders reports insights correctly', () => {
      const initialState = {
        reportsInsights: {
          comprehensive: {
            cost_analysis: {
              trend: 'Decreasing',
              summary: 'Costs are trending downward due to improved efficiency',
            },
            predictions_summary: {
              total_predictions: 150,
            },
            last_updated: '2024-01-15T10:30:00Z',
          },
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights
            type="reports"
            reportType="comprehensive"
            title="AI Report Intelligence"
            showRefresh={true}
            onRefresh={mockOnRefresh}
          />
        </TestWrapper>
      );

      expect(screen.getByText('AI Report Intelligence')).toBeInTheDocument();
      expect(screen.getByText('Decreasing')).toBeInTheDocument();
      expect(screen.getByText('Costs are trending downward due to improved efficiency')).toBeInTheDocument();
      expect(screen.getByText('150')).toBeInTheDocument();
      expect(screen.getByText('Total predictions generated')).toBeInTheDocument();
    });
  });

  describe('Refresh Functionality', () => {
    it('calls onRefresh when refresh button is clicked', () => {
      const initialState = {
        dashboardInsights: {
          cost_predictions: { total_predicted_cost: 1000000 },
          last_updated: '2024-01-15T10:30:00Z',
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights
            type="dashboard"
            title="AI-Powered Insights"
            showRefresh={true}
            onRefresh={mockOnRefresh}
          />
        </TestWrapper>
      );

      const refreshButton = screen.getByRole('button', { name: /refresh insights/i });
      fireEvent.click(refreshButton);

      expect(mockOnRefresh).toHaveBeenCalledTimes(1);
    });

    it('does not show refresh button when showRefresh is false', () => {
      const initialState = {
        dashboardInsights: {
          cost_predictions: { total_predicted_cost: 1000000 },
          last_updated: '2024-01-15T10:30:00Z',
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights
            type="dashboard"
            title="AI-Powered Insights"
            showRefresh={false}
            onRefresh={mockOnRefresh}
          />
        </TestWrapper>
      );

      expect(screen.queryByRole('button', { name: /refresh insights/i })).not.toBeInTheDocument();
    });
  });

  describe('Last Updated Display', () => {
    it('displays last updated timestamp when available', () => {
      const initialState = {
        dashboardInsights: {
          cost_predictions: { total_predicted_cost: 1000000 },
          last_updated: '2024-01-15T10:30:00Z',
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights type="dashboard" title="AI-Powered Insights" />
        </TestWrapper>
      );

      expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
      expect(screen.getByText(/1\/15\/2024/)).toBeInTheDocument();
    });

    it('does not display last updated when not available', () => {
      const initialState = {
        dashboardInsights: {
          cost_predictions: { total_predicted_cost: 1000000 },
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights type="dashboard" title="AI-Powered Insights" />
        </TestWrapper>
      );

      expect(screen.queryByText(/Last updated:/)).not.toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles missing data gracefully', () => {
      const initialState = {
        dashboardInsights: {
          cost_predictions: null,
          risk_insights: undefined,
          timeline_predictions: {},
        },
      };

      render(
        <TestWrapper initialState={initialState}>
          <MLInsights type="dashboard" title="AI-Powered Insights" />
        </TestWrapper>
      );

      expect(screen.getByText('AI-Powered Insights')).toBeInTheDocument();
      // Should not crash and should handle missing data gracefully
    });
  });
});
