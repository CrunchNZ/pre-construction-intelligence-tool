import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
} from '@mui/material';
import { Chart } from '../../components/common';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('6months');
  const [selectedProject, setSelectedProject] = useState('all');
  const [loading, setLoading] = useState(false);

  // Mock analytics data - replace with actual API calls
  const analyticsData = {
    costTrends: [
      { month: 'Jan', budget: 2.5, actual: 2.3, variance: -8.0 },
      { month: 'Feb', budget: 2.8, actual: 2.9, variance: 3.6 },
      { month: 'Mar', budget: 3.2, actual: 3.4, variance: 6.3 },
      { month: 'Apr', budget: 3.5, actual: 3.7, variance: 5.7 },
      { month: 'May', budget: 3.8, actual: 4.1, variance: 7.9 },
      { month: 'Jun', budget: 4.2, actual: 4.5, variance: 7.1 },
    ],
    
    projectPerformance: [
      { name: 'Hospital Extension', budget: 25.0, actual: 26.5, progress: 65, risk: 'medium' },
      { name: 'Office Complex', budget: 18.0, actual: 0, progress: 0, risk: 'low' },
      { name: 'Residential Tower', budget: 32.0, actual: 0, progress: 0, risk: 'high' },
      { name: 'Shopping Center', budget: 15.0, actual: 14.2, progress: 100, risk: 'low' },
    ],
    
    riskDistribution: [
      { name: 'Cost Risk', value: 35, color: '#ff6b6b' },
      { name: 'Schedule Risk', value: 25, color: '#4ecdc4' },
      { name: 'Quality Risk', value: 20, color: '#45b7d1' },
      { name: 'Supply Chain', value: 15, color: '#96ceb4' },
      { name: 'Weather Risk', value: 5, color: '#feca57' },
    ],
    
    supplierPerformance: [
      { name: 'Excellent', value: 45, color: '#2ecc71' },
      { name: 'Good', value: 35, color: '#3498db' },
      { name: 'Average', value: 15, color: '#f39c12' },
      { name: 'Poor', value: 5, color: '#e74c3c' },
    ],
    
    monthlyProgress: [
      { month: 'Jan', planned: 15, actual: 14, efficiency: 93.3 },
      { month: 'Feb', planned: 18, actual: 17, efficiency: 94.4 },
      { month: 'Mar', planned: 22, actual: 20, efficiency: 90.9 },
      { month: 'Apr', planned: 25, actual: 23, efficiency: 92.0 },
      { month: 'May', planned: 28, actual: 26, efficiency: 92.9 },
      { month: 'Jun', planned: 30, actual: 28, efficiency: 93.3 },
    ],
    
    costBreakdown: [
      { category: 'Materials', budget: 40, actual: 42, variance: 5.0 },
      { category: 'Labor', budget: 35, actual: 36, variance: 2.9 },
      { category: 'Equipment', budget: 15, actual: 14, variance: -6.7 },
      { category: 'Subcontractors', budget: 10, actual: 11, variance: 10.0 },
    ],
  };

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange, selectedProject]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Simulate API call with filters
      await new Promise(resolve => setTimeout(resolve, 1000));
      // In real implementation, fetch data based on timeRange and selectedProject
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getVarianceColor = (variance) => {
    if (variance > 10) return 'error';
    if (variance > 5) return 'warning';
    if (variance < 0) return 'success';
    return 'info';
  };

  const getRiskColor = (risk) => {
    const colors = { low: 'success', medium: 'warning', high: 'error' };
    return colors[risk] || 'default';
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Analytics & Insights
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Comprehensive analysis of project performance, costs, and risks
          </Typography>
        </Box>
        
        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="3months">Last 3 Months</MenuItem>
              <MenuItem value="6months">Last 6 Months</MenuItem>
              <MenuItem value="1year">Last Year</MenuItem>
              <MenuItem value="all">All Time</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Project</InputLabel>
            <Select
              value={selectedProject}
              label="Project"
              onChange={(e) => setSelectedProject(e.target.value)}
            >
              <MenuItem value="all">All Projects</MenuItem>
              <MenuItem value="hospital">Hospital Extension</MenuItem>
              <MenuItem value="office">Office Complex</MenuItem>
              <MenuItem value="residential">Residential Tower</MenuItem>
              <MenuItem value="shopping">Shopping Center</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Key Metrics Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Key Insight:</strong> Overall project efficiency is at 93.2% with a cost variance of 6.8%. 
          The Hospital Extension project shows the highest cost variance at 6.0% and should be monitored closely.
        </Typography>
      </Alert>

      {/* Cost Trends Chart */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} lg={8}>
          <Chart
            title="Cost Trends & Variance"
            data={analyticsData.costTrends}
            type="line"
            height={400}
            loading={loading}
            onRefresh={loadAnalyticsData}
            chartProps={{
              margin: { top: 20, right: 30, left: 20, bottom: 5 },
            }}
          />
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <Chart
            title="Risk Distribution"
            data={analyticsData.riskDistribution}
            type="pie"
            height={400}
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Project Performance & Supplier Performance */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} lg={6}>
          <Chart
            title="Project Performance Overview"
            data={analyticsData.projectPerformance}
            type="bar"
            height={350}
            loading={loading}
            chartProps={{
              margin: { top: 20, right: 30, left: 20, bottom: 5 },
            }}
          />
        </Grid>
        
        <Grid item xs={12} lg={6}>
          <Chart
            title="Supplier Performance Rating"
            data={analyticsData.supplierPerformance}
            type="bar"
            height={350}
            loading={loading}
            colors={['#2ecc71', '#3498db', '#f39c12', '#e74c3c']}
          />
        </Grid>
      </Grid>

      {/* Monthly Progress & Cost Breakdown */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} lg={6}>
          <Chart
            title="Monthly Progress vs Planned"
            data={analyticsData.monthlyProgress}
            type="area"
            height={350}
            loading={loading}
            chartProps={{
              margin: { top: 20, right: 30, left: 20, bottom: 5 },
            }}
          />
        </Grid>
        
        <Grid item xs={12} lg={6}>
          <Chart
            title="Cost Breakdown by Category"
            data={analyticsData.costBreakdown}
            type="bar"
            height={350}
            loading={loading}
            chartProps={{
              margin: { top: 20, right: 30, left: 20, bottom: 5 },
            }}
          />
        </Grid>
      </Grid>

      {/* Detailed Project Analysis */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Project Performance Analysis
              </Typography>
              
              <Grid container spacing={2}>
                {analyticsData.projectPerformance.map((project) => (
                  <Grid item xs={12} sm={6} md={3} key={project.name}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="subtitle2" fontWeight="medium" gutterBottom>
                          {project.name}
                        </Typography>
                        
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="caption" color="text.secondary">
                            Budget: ${project.budget}M
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Actual: ${project.actual}M
                          </Typography>
                        </Box>
                        
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="caption" color="text.secondary">
                            Progress: {project.progress}%
                          </Typography>
                          <Chip
                            label={project.risk}
                            color={getRiskColor(project.risk)}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                        
                        {project.actual > 0 && (
                          <Typography
                            variant="caption"
                            color={getVarianceColor(((project.actual - project.budget) / project.budget) * 100)}
                            fontWeight="medium"
                          >
                            Variance: {((project.actual - project.budget) / project.budget * 100).toFixed(1)}%
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
