import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Business as BusinessIcon,
  People as PeopleIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useSelector, useDispatch } from 'react-redux';
import MLInsights from '../../components/common/MLInsights';
import { fetchDashboardInsights } from '../../store/slices/mlInsightsSlice';

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const dispatch = useDispatch();
  
  // Mock data for demonstration - replace with actual API calls
  const mockData = {
    summary: {
      totalProjects: 45,
      activeProjects: 12,
      completedProjects: 28,
      totalSuppliers: 156,
      activeSuppliers: 89,
      totalRisks: 23,
      highRisks: 7,
    },
    costAnalysis: {
      averageVariance: 12.5,
      projectsOverBudget: 8,
      totalSavings: 1250000,
    },
    recentProjects: [
      { id: 1, name: 'Hospital Extension', status: 'execution', costVariance: 8.2, type: 'healthcare' },
      { id: 2, name: 'Office Complex', status: 'bidding', costVariance: -2.1, type: 'commercial' },
      { id: 3, name: 'Residential Tower', status: 'planning', costVariance: 0, type: 'residential' },
      { id: 4, name: 'Shopping Center', status: 'completed', costVariance: 15.3, type: 'commercial' },
    ],
    costTrends: [
      { month: 'Jan', variance: 8.2, projects: 12 },
      { month: 'Feb', variance: 12.1, projects: 15 },
      { month: 'Mar', variance: 9.8, projects: 18 },
      { month: 'Apr', variance: 11.5, projects: 22 },
      { month: 'May', variance: 7.9, projects: 25 },
      { month: 'Jun', variance: 10.3, projects: 28 },
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
  };

  useEffect(() => {
    // Load dashboard data
    loadDashboardData();
    // Load ML insights
    dispatch(fetchDashboardInsights());
  }, [dispatch]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setDashboardData(mockData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      planning: 'info',
      bidding: 'warning',
      execution: 'primary',
      completed: 'success',
      cancelled: 'error',
    };
    return colors[status] || 'default';
  };

  const getVarianceColor = (variance) => {
    if (variance > 10) return 'error';
    if (variance > 5) return 'warning';
    if (variance < 0) return 'success';
    return 'default';
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      {/* ML Insights Section */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <MLInsights
            type="dashboard"
            title="AI-Powered Insights"
            showRefresh={true}
            onRefresh={() => dispatch(fetchDashboardInsights())}
          />
        </Grid>
      </Grid>

      {/* Existing Dashboard Content */}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <BusinessIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4" component="div">
                      {dashboardData?.summary.totalProjects || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Projects
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <PeopleIcon color="secondary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4" component="div">
                      {dashboardData?.summary.totalSuppliers || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Suppliers
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <WarningIcon color="error" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h4" component="div">
                      {dashboardData?.summary.totalRisks || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active Risks
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <TrendingUpIcon 
                    color={dashboardData?.costAnalysis.averageVariance > 10 ? "error" : "success"} 
                    sx={{ mr: 1 }} 
                  />
                  <Box>
                    <Typography variant="h4" component="div">
                      {dashboardData?.costAnalysis.averageVariance || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Cost Variance
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Charts Row */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Cost Trends Chart */}
            <Grid item xs={12} lg={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cost Variance Trends
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={dashboardData?.costTrends || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line 
                        type="monotone" 
                        dataKey="variance" 
                        stroke="#1976d2" 
                        strokeWidth={2}
                        name="Cost Variance %"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="projects" 
                        stroke="#dc004e" 
                        strokeWidth={2}
                        name="Active Projects"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Risk Distribution */}
            <Grid item xs={12} lg={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Risk Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={dashboardData?.riskDistribution || []}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {dashboardData?.riskDistribution?.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Recent Projects and Supplier Performance */}
          <Grid container spacing={3}>
            {/* Recent Projects */}
            <Grid item xs={12} lg={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Projects
                  </Typography>
                  <Box>
                    {dashboardData?.recentProjects?.map((project) => (
                      <Box
                        key={project.id}
                        display="flex"
                        justifyContent="space-between"
                        alignItems="center"
                        py={1}
                        borderBottom="1px solid #f0f0f0"
                      >
                        <Box>
                          <Typography variant="body1" fontWeight="medium">
                            {project.name}
                          </Typography>
                          <Box display="flex" gap={1} mt={0.5}>
                            <Chip 
                              label={project.status} 
                              color={getStatusColor(project.status)} 
                              size="small" 
                            />
                            <Chip 
                              label={project.type} 
                              variant="outlined" 
                              size="small" 
                            />
                          </Box>
                        </Box>
                        <Box textAlign="right">
                          <Typography 
                            variant="body2" 
                            color={getVarianceColor(project.costVariance)}
                            fontWeight="medium"
                          >
                            {project.costVariance > 0 ? '+' : ''}{project.costVariance}%
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Cost Variance
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Supplier Performance */}
            <Grid item xs={12} lg={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Supplier Performance
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dashboardData?.supplierPerformance || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="value" fill="#8884d8">
                        {dashboardData?.supplierPerformance?.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard;
