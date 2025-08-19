import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import mlService from '../../services/mlService';

// Async thunks for fetching ML insights
export const fetchDashboardInsights = createAsyncThunk(
  'mlInsights/fetchDashboardInsights',
  async (_, { rejectWithValue }) => {
    try {
      const insights = await mlService.getDashboardInsights();
      return insights;
    } catch (error) {
      return rejectWithValue(mlService.handleError(error));
    }
  }
);

export const fetchProjectInsights = createAsyncThunk(
  'mlInsights/fetchProjectInsights',
  async (projectId, { rejectWithValue }) => {
    try {
      const insights = await mlService.getProjectInsights(projectId);
      return { projectId, insights };
    } catch (error) {
      return rejectWithValue({ projectId, error: mlService.handleError(error) });
    }
  }
);

export const fetchRiskAnalysisInsights = createAsyncThunk(
  'mlInsights/fetchRiskAnalysisInsights',
  async (_, { rejectWithValue }) => {
    try {
      const insights = await mlService.getRiskAnalysisInsights();
      return insights;
    } catch (error) {
      return rejectWithValue(mlService.handleError(error));
    }
  }
);

export const fetchReportsInsights = createAsyncThunk(
  'mlInsights/fetchReportsInsights',
  async (reportType = 'comprehensive', { rejectWithValue }) => {
    try {
      const insights = await mlService.getReportsInsights(reportType);
      return { reportType, insights };
    } catch (error) {
      return rejectWithValue({ reportType, error: mlService.handleError(error) });
    }
  }
);

export const fetchModelPerformance = createAsyncThunk(
  'mlInsights/fetchModelPerformance',
  async (_, { rejectWithValue }) => {
    try {
      const performance = await mlService.getModelPerformance();
      return performance;
    } catch (error) {
      return rejectWithValue(mlService.handleError(error));
    }
  }
);

export const fetchAccuracyAnalysis = createAsyncThunk(
  'mlInsights/fetchAccuracyAnalysis',
  async ({ modelId, days = 30 }, { rejectWithValue }) => {
    try {
      const analysis = await mlService.getAccuracyAnalysis(modelId, days);
      return { modelId, days, analysis };
    } catch (error) {
      return rejectWithValue({ modelId, days, error: mlService.handleError(error) });
    }
  }
);

const initialState = {
  // Dashboard insights
  dashboardInsights: null,
  dashboardLoading: false,
  dashboardError: null,
  
  // Project insights (cached by project ID)
  projectInsights: {},
  projectInsightsLoading: {},
  projectInsightsError: {},
  
  // Risk analysis insights
  riskAnalysisInsights: null,
  riskAnalysisLoading: false,
  riskAnalysisError: null,
  
  // Reports insights (cached by report type)
  reportsInsights: {},
  reportsInsightsLoading: {},
  reportsInsightsError: {},
  
  // Model performance
  modelPerformance: null,
  modelPerformanceLoading: false,
  modelPerformanceError: null,
  
  // Accuracy analysis (cached by model ID and days)
  accuracyAnalysis: {},
  accuracyAnalysisLoading: {},
  accuracyAnalysisError: {},
  
  // Global state
  lastUpdated: null,
};

const mlInsightsSlice = createSlice({
  name: 'mlInsights',
  initialState,
  reducers: {
    clearProjectInsights: (state, action) => {
      const projectId = action.payload;
      delete state.projectInsights[projectId];
      delete state.projectInsightsLoading[projectId];
      delete state.projectInsightsError[projectId];
    },
    
    clearReportsInsights: (state, action) => {
      const reportType = action.payload;
      delete state.reportsInsights[reportType];
      delete state.reportsInsightsLoading[reportType];
      delete state.reportsInsightsError[reportType];
    },
    
    clearAccuracyAnalysis: (state, action) => {
      const { modelId, days } = action.payload;
      const key = `${modelId || 'all'}_${days}`;
      delete state.accuracyAnalysis[key];
      delete state.accuracyAnalysisLoading[key];
      delete state.accuracyAnalysisError[key];
    },
    
    clearAllInsights: (state) => {
      state.dashboardInsights = null;
      state.projectInsights = {};
      state.riskAnalysisInsights = null;
      state.reportsInsights = {};
      state.modelPerformance = null;
      state.accuracyAnalysis = {};
      state.lastUpdated = null;
    },
  },
  extraReducers: (builder) => {
    // Dashboard insights
    builder
      .addCase(fetchDashboardInsights.pending, (state) => {
        state.dashboardLoading = true;
        state.dashboardError = null;
      })
      .addCase(fetchDashboardInsights.fulfilled, (state, action) => {
        state.dashboardLoading = false;
        state.dashboardInsights = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchDashboardInsights.rejected, (state, action) => {
        state.dashboardLoading = false;
        state.dashboardError = action.payload;
      });
    
    // Project insights
    builder
      .addCase(fetchProjectInsights.pending, (state, action) => {
        const projectId = action.meta.arg;
        state.projectInsightsLoading[projectId] = true;
        state.projectInsightsError[projectId] = null;
      })
      .addCase(fetchProjectInsights.fulfilled, (state, action) => {
        const { projectId, insights } = action.payload;
        state.projectInsightsLoading[projectId] = false;
        state.projectInsights[projectId] = insights;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchProjectInsights.rejected, (state, action) => {
        const { projectId, error } = action.payload;
        state.projectInsightsLoading[projectId] = false;
        state.projectInsightsError[projectId] = error;
      });
    
    // Risk analysis insights
    builder
      .addCase(fetchRiskAnalysisInsights.pending, (state) => {
        state.riskAnalysisLoading = true;
        state.riskAnalysisError = null;
      })
      .addCase(fetchRiskAnalysisInsights.fulfilled, (state, action) => {
        state.riskAnalysisLoading = false;
        state.riskAnalysisInsights = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchRiskAnalysisInsights.rejected, (state, action) => {
        state.riskAnalysisLoading = false;
        state.riskAnalysisError = action.payload;
      });
    
    // Reports insights
    builder
      .addCase(fetchReportsInsights.pending, (state, action) => {
        const reportType = action.meta.arg;
        state.reportsInsightsLoading[reportType] = true;
        state.reportsInsightsError[reportType] = null;
      })
      .addCase(fetchReportsInsights.fulfilled, (state, action) => {
        const { reportType, insights } = action.payload;
        state.reportsInsightsLoading[reportType] = false;
        state.reportsInsights[reportType] = insights;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchReportsInsights.rejected, (state, action) => {
        const { reportType, error } = action.payload;
        state.reportsInsightsLoading[reportType] = false;
        state.reportsInsightsError[reportType] = error;
      });
    
    // Model performance
    builder
      .addCase(fetchModelPerformance.pending, (state) => {
        state.modelPerformanceLoading = true;
        state.modelPerformanceError = null;
      })
      .addCase(fetchModelPerformance.fulfilled, (state, action) => {
        state.modelPerformanceLoading = false;
        state.modelPerformance = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchModelPerformance.rejected, (state, action) => {
        state.modelPerformanceLoading = false;
        state.modelPerformanceError = action.payload;
      });
    
    // Accuracy analysis
    builder
      .addCase(fetchAccuracyAnalysis.pending, (state, action) => {
        const { modelId, days } = action.meta.arg;
        const key = `${modelId || 'all'}_${days}`;
        state.accuracyAnalysisLoading[key] = true;
        state.accuracyAnalysisError[key] = null;
      })
      .addCase(fetchAccuracyAnalysis.fulfilled, (state, action) => {
        const { modelId, days, analysis } = action.payload;
        const key = `${modelId || 'all'}_${days}`;
        state.accuracyAnalysisLoading[key] = false;
        state.accuracyAnalysis[key] = analysis;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchAccuracyAnalysis.rejected, (state, action) => {
        const { modelId, days, error } = action.payload;
        const key = `${modelId || 'all'}_${days}`;
        state.accuracyAnalysisLoading[key] = false;
        state.accuracyAnalysisError[key] = error;
      });
  },
});

// Export actions
export const {
  clearProjectInsights,
  clearReportsInsights,
  clearAccuracyAnalysis,
  clearAllInsights,
} = mlInsightsSlice.actions;

// Export selectors
export const selectDashboardInsights = (state) => state.mlInsights.dashboardInsights;
export const selectDashboardLoading = (state) => state.mlInsights.dashboardLoading;
export const selectDashboardError = (state) => state.mlInsights.dashboardError;

export const selectProjectInsights = (state, projectId) => state.mlInsights.projectInsights[projectId];
export const selectProjectInsightsLoading = (state, projectId) => state.mlInsights.projectInsightsLoading[projectId];
export const selectProjectInsightsError = (state, projectId) => state.mlInsights.projectInsightsError[projectId];

export const selectRiskAnalysisInsights = (state) => state.mlInsights.riskAnalysisInsights;
export const selectRiskAnalysisLoading = (state) => state.mlInsights.riskAnalysisLoading;
export const selectRiskAnalysisError = (state) => state.mlInsights.riskAnalysisError;

export const selectReportsInsights = (state, reportType) => state.mlInsights.reportsInsights[reportType];
export const selectReportsInsightsLoading = (state, reportType) => state.mlInsights.reportsInsightsLoading[reportType];
export const selectReportsInsightsError = (state, reportType) => state.mlInsights.reportsInsightsError[reportType];

export const selectModelPerformance = (state) => state.mlInsights.modelPerformance;
export const selectModelPerformanceLoading = (state) => state.mlInsights.modelPerformanceLoading;
export const selectModelPerformanceError = (state) => state.mlInsights.modelPerformanceError;

export const selectAccuracyAnalysis = (state, modelId, days = 30) => {
  const key = `${modelId || 'all'}_${days}`;
  return state.mlInsights.accuracyAnalysis[key];
};
export const selectAccuracyAnalysisLoading = (state, modelId, days = 30) => {
  const key = `${modelId || 'all'}_${days}`;
  return state.mlInsights.accuracyAnalysisLoading[key];
};
export const selectAccuracyAnalysisError = (state, modelId, days = 30) => {
  const key = `${modelId || 'all'}_${days}`;
  return state.mlInsights.accuracyAnalysisError[key];
};

export const selectLastUpdated = (state) => state.mlInsights.lastUpdated;

export default mlInsightsSlice.reducer;
