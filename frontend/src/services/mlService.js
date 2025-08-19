/**
 * ML Service for fetching AI/ML insights from the backend
 * Provides methods to integrate ML predictions and insights with frontend components
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class MLService {
  /**
   * Get ML insights for the dashboard
   * @returns {Promise<Object>} Dashboard ML insights
   */
  async getDashboardInsights() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-models/models/dashboard_insights/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching dashboard ML insights:', error);
      throw error;
    }
  }

  /**
   * Get ML insights for a specific project
   * @param {number} projectId - The project ID
   * @returns {Promise<Object>} Project ML insights
   */
  async getProjectInsights(projectId) {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-models/models/project_insights/?project_id=${projectId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching project ML insights:', error);
      throw error;
    }
  }

  /**
   * Get ML insights for risk analysis
   * @returns {Promise<Object>} Risk analysis ML insights
   */
  async getRiskAnalysisInsights() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-models/models/risk_analysis_insights/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching risk analysis ML insights:', error);
      throw error;
    }
  }

  /**
   * Get ML insights for reports
   * @param {string} reportType - Type of report ('comprehensive', 'cost', 'timeline', 'risk', 'quality')
   * @returns {Promise<Object>} Reports ML insights
   */
  async getReportsInsights(reportType = 'comprehensive') {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-models/models/reports_insights/?report_type=${reportType}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching reports ML insights:', error);
      throw error;
    }
  }

  /**
   * Get ML model performance summary
   * @returns {Promise<Object>} Model performance data
   */
  async getModelPerformance() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-models/models/performance_summary/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching model performance:', error);
      throw error;
    }
  }

  /**
   * Get prediction accuracy analysis
   * @param {number} modelId - Optional model ID to filter by
   * @param {number} days - Number of days to analyze (default: 30)
   * @returns {Promise<Object>} Accuracy analysis data
   */
  async getAccuracyAnalysis(modelId = null, days = 30) {
    try {
      let url = `${API_BASE_URL}/ai-models/predictions/accuracy_analysis/?days=${days}`;
      if (modelId) {
        url += `&model_id=${modelId}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching accuracy analysis:', error);
      throw error;
    }
  }

  /**
   * Get authentication token from localStorage or other auth storage
   * @returns {string} Auth token
   */
  getAuthToken() {
    // This should be implemented based on your authentication system
    // For now, returning a placeholder
    return localStorage.getItem('authToken') || '';
  }

  /**
   * Handle API errors and provide user-friendly error messages
   * @param {Error} error - The error object
   * @returns {string} User-friendly error message
   */
  handleError(error) {
    if (error.message.includes('401')) {
      return 'Authentication required. Please log in again.';
    } else if (error.message.includes('403')) {
      return 'Access denied. You do not have permission to view this data.';
    } else if (error.message.includes('404')) {
      return 'The requested data was not found.';
    } else if (error.message.includes('500')) {
      return 'Server error. Please try again later.';
    } else {
      return 'An unexpected error occurred. Please try again.';
    }
  }
}

// Create and export a singleton instance
const mlService = new MLService();
export default mlService;
