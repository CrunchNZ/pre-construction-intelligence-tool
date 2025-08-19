import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Grid,
  Divider,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';

/**
 * ML Insights Component
 * Displays AI/ML predictions and insights in a consistent format
 */
const MLInsights = ({
  type = 'dashboard', // 'dashboard', 'project', 'risk', 'reports'
  projectId = null,
  reportType = 'comprehensive',
  title = 'AI Insights',
  showRefresh = true,
  onRefresh = null,
  className = '',
}) => {
  const dispatch = useDispatch();
  
  // Select appropriate data based on type
  const getInsightsData = () => {
    switch (type) {
      case 'dashboard':
        return {
          data: useSelector(state => state.mlInsights.dashboardInsights),
          loading: useSelector(state => state.mlInsights.dashboardLoading),
          error: useSelector(state => state.mlInsights.dashboardError),
        };
      case 'project':
        return {
          data: useSelector(state => state.mlInsights.projectInsights[projectId]),
          loading: useSelector(state => state.mlInsights.projectInsightsLoading[projectId]),
          error: useSelector(state => state.mlInsights.projectInsightsError[projectId]),
        };
      case 'risk':
        return {
          data: useSelector(state => state.mlInsights.riskAnalysisInsights),
          loading: useSelector(state => state.mlInsights.riskAnalysisLoading),
          error: useSelector(state => state.mlInsights.riskAnalysisError),
        };
      case 'reports':
        return {
          data: useSelector(state => state.mlInsights.reportsInsights[reportType]),
          loading: useSelector(state => state.mlInsights.reportsInsightsLoading[reportType]),
          error: useSelector(state => state.mlInsights.reportsInsightsError[reportType]),
        };
      default:
        return { data: null, loading: false, error: null };
    }
  };

  const { data, loading, error } = getInsightsData();

  // Handle refresh
  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    }
  };

  // Render loading state
  if (loading) {
    return (
      <Card className={className}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <PsychologyIcon color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h3">
              {title}
            </Typography>
            {showRefresh && (
              <IconButton size="small" onClick={handleRefresh} sx={{ ml: 'auto' }}>
                <RefreshIcon />
              </IconButton>
            )}
          </Box>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Loading AI insights...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Render error state
  if (error) {
    return (
      <Card className={className}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <PsychologyIcon color="error" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h3">
              {title}
            </Typography>
            {showRefresh && (
              <IconButton size="small" onClick={handleRefresh} sx={{ ml: 'auto' }}>
                <RefreshIcon />
              </IconButton>
            )}
          </Box>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Typography variant="body2" color="text.secondary">
            Unable to load AI insights. Please try refreshing.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Render no data state
  if (!data || Object.keys(data).length === 0) {
    return (
      <Card className={className}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <PsychologyIcon color="action" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h3">
              {title}
            </Typography>
            {showRefresh && (
              <IconButton size="small" onClick={handleRefresh} sx={{ ml: 'auto' }}>
                <RefreshIcon />
              </IconButton>
            )}
          </Box>
          <Typography variant="body2" color="text.secondary">
            No AI insights available at this time.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Render insights based on type
  const renderInsights = () => {
    switch (type) {
      case 'dashboard':
        return renderDashboardInsights(data);
      case 'project':
        return renderProjectInsights(data);
      case 'risk':
        return renderRiskInsights(data);
      case 'reports':
        return renderReportsInsights(data);
      default:
        return renderGenericInsights(data);
    }
  };

  const renderDashboardInsights = (insights) => (
    <Grid container spacing={2}>
      {insights.cost_predictions && (
        <Grid item xs={12} sm={6} md={4}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Cost Predictions
            </Typography>
            <Typography variant="h6" color="primary">
              ${insights.cost_predictions.total_predicted_cost?.toLocaleString() || 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Confidence: {(insights.cost_predictions.avg_prediction_confidence * 100).toFixed(1)}%
            </Typography>
          </Box>
        </Grid>
      )}
      
      {insights.risk_insights && (
        <Grid item xs={12} sm={6} md={4}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Risk Assessment
            </Typography>
            <Typography variant="h6" color="error">
              {insights.risk_insights.high_risk_count || 0} High Risk
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total: {insights.risk_insights.total_risks || 0}
            </Typography>
          </Box>
        </Grid>
      )}
      
      {insights.timeline_predictions && (
        <Grid item xs={12} sm={6} md={4}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Timeline Predictions
            </Typography>
            <Typography variant="h6" color="info">
              {insights.timeline_predictions.avg_prediction_confidence ? 
                `${(insights.timeline_predictions.avg_prediction_confidence * 100).toFixed(1)}%` : 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Accuracy
            </Typography>
          </Box>
        </Grid>
      )}
    </Grid>
  );

  const renderProjectInsights = (insights) => (
    <Grid container spacing={2}>
      {insights.cost_prediction && (
        <Grid item xs={12} sm={6}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Cost Prediction
            </Typography>
            <Typography variant="h6" color="primary">
              ${insights.cost_prediction.predicted_cost?.toLocaleString() || 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Confidence: {(insights.cost_prediction.confidence * 100).toFixed(1)}%
            </Typography>
          </Box>
        </Grid>
      )}
      
      {insights.timeline_prediction && (
        <Grid item xs={12} sm={6}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Timeline Prediction
            </Typography>
            <Typography variant="h6" color="info">
              {insights.timeline_prediction.predicted_duration || 'N/A'} days
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Confidence: {(insights.timeline_prediction.confidence * 100).toFixed(1)}%
            </Typography>
          </Box>
        </Grid>
      )}
      
      {insights.risk_assessment && (
        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Risk Assessment
          </Typography>
          <Chip
            label={insights.risk_assessment.risk_level || 'Unknown'}
            color={insights.risk_assessment.risk_level === 'high' ? 'error' : 
                   insights.risk_assessment.risk_level === 'medium' ? 'warning' : 'success'}
            sx={{ mb: 1 }}
          />
          <Typography variant="body2" color="text.secondary">
            {insights.risk_assessment.description || 'No risk description available'}
          </Typography>
        </Grid>
      )}
    </Grid>
  );

  const renderRiskInsights = (insights) => (
    <Grid container spacing={2}>
      {insights.overall_risk_score && (
        <Grid item xs={12} sm={6}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Overall Risk Score
            </Typography>
            <Typography variant="h6" color="error">
              {insights.overall_risk_score.toFixed(1)}/10
            </Typography>
            <LinearProgress
              variant="determinate"
              value={insights.overall_risk_score * 10}
              color="error"
              sx={{ mt: 1 }}
            />
          </Box>
        </Grid>
      )}
      
      {insights.high_risk_projects && (
        <Grid item xs={12} sm={6}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              High Risk Projects
            </Typography>
            <Typography variant="h6" color="error">
              {insights.high_risk_projects.length || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Require immediate attention
            </Typography>
          </Box>
        </Grid>
      )}
    </Grid>
  );

  const renderReportsInsights = (insights) => (
    <Grid container spacing={2}>
      {insights.cost_analysis && (
        <Grid item xs={12} sm={6}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Cost Analysis
            </Typography>
            <Typography variant="h6" color="primary">
              {insights.cost_analysis.trend || 'N/A'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {insights.cost_analysis.summary || 'No cost analysis available'}
            </Typography>
          </Box>
        </Grid>
      )}
      
      {insights.predictions_summary && (
        <Grid item xs={12} sm={6}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Predictions Summary
            </Typography>
            <Typography variant="h6" color="info">
              {insights.predictions_summary.total_predictions || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total predictions generated
            </Typography>
          </Box>
        </Grid>
      )}
    </Grid>
  );

  const renderGenericInsights = (insights) => (
    <Box>
      <Typography variant="body2" color="text.secondary">
        {JSON.stringify(insights, null, 2)}
      </Typography>
    </Box>
  );

  return (
    <Card className={className}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <PsychologyIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6" component="h3">
            {title}
          </Typography>
          {showRefresh && (
            <Tooltip title="Refresh insights">
              <IconButton size="small" onClick={handleRefresh} sx={{ ml: 'auto' }}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        {renderInsights()}
        
        {data.last_updated && (
          <Box mt={2} pt={2} borderTop="1px solid" borderColor="divider">
            <Typography variant="caption" color="text.secondary">
              Last updated: {new Date(data.last_updated).toLocaleString()}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default MLInsights;
