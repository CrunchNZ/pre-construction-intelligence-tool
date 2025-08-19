import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { Chart, Modal, Form, Notification } from '../../components/common';
import MLInsights from '../../components/common/MLInsights';
import { fetchRiskAnalysisInsights } from '../../store/slices/mlInsightsSlice';

const RiskAnalysis = () => {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRisk, setEditingRisk] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [activeTab, setActiveTab] = useState(0);
  const dispatch = useDispatch();

  // Mock data - replace with actual API calls
  const mockRisks = [
    {
      id: 1,
      title: 'Material Price Volatility',
      category: 'Financial',
      severity: 'High',
      probability: 75,
      impact: 90,
      riskScore: 68,
      status: 'Active',
      project: 'Downtown Office Complex',
      description: 'Steel and concrete prices are experiencing significant fluctuations due to supply chain disruptions.',
      mitigation: 'Lock in prices with suppliers, establish price escalation clauses in contracts.',
      owner: 'John Smith',
      dueDate: '2024-02-15',
      lastAssessment: '2024-01-10',
      trend: 'increasing',
    },
    {
      id: 2,
      title: 'Labor Shortage',
      category: 'Operational',
      severity: 'Medium',
      probability: 60,
      impact: 70,
      riskScore: 42,
      status: 'Mitigated',
      project: 'Healthcare Facility',
      description: 'Skilled labor shortage in the region may delay project completion.',
      mitigation: 'Partner with local trade schools, offer competitive wages, cross-train existing workers.',
      owner: 'Sarah Johnson',
      dueDate: '2024-03-01',
      lastAssessment: '2024-01-08',
      trend: 'decreasing',
    },
    {
      id: 3,
      title: 'Weather Delays',
      category: 'Environmental',
      severity: 'Medium',
      probability: 80,
      impact: 50,
      riskScore: 40,
      status: 'Active',
      project: 'Infrastructure Project',
      description: 'Unpredictable weather patterns may cause construction delays.',
      mitigation: 'Implement flexible scheduling, use weather-resistant materials, plan for buffer time.',
      owner: 'Mike Davis',
      dueDate: '2024-02-28',
      lastAssessment: '2024-01-12',
      trend: 'stable',
    },
    {
      id: 4,
      title: 'Regulatory Changes',
      category: 'Compliance',
      severity: 'Low',
      probability: 30,
      impact: 60,
      riskScore: 18,
      status: 'Monitored',
      project: 'All Projects',
      description: 'Potential changes in building codes and safety regulations.',
      mitigation: 'Stay updated with regulatory bodies, engage with industry associations.',
      owner: 'Lisa Chen',
      dueDate: '2024-04-01',
      lastAssessment: '2024-01-05',
      trend: 'stable',
    },
    {
      id: 5,
      title: 'Equipment Failure',
      category: 'Technical',
      severity: 'High',
      probability: 40,
      impact: 85,
      riskScore: 34,
      status: 'Active',
      project: 'Industrial Plant',
      description: 'Critical equipment may fail during peak construction periods.',
      mitigation: 'Implement preventive maintenance schedule, maintain spare parts inventory.',
      owner: 'Tom Wilson',
      dueDate: '2024-02-20',
      lastAssessment: '2024-01-09',
      trend: 'increasing',
    },
  ];

  useEffect(() => {
    loadRisks();
    // Load ML insights
    dispatch(fetchRiskAnalysisInsights());
  }, [dispatch]);

  const loadRisks = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setRisks(mockRisks);
    } catch (error) {
      showNotification('Failed to load risks', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleAddRisk = () => {
    setEditingRisk(null);
    setModalOpen(true);
  };

  const handleEditRisk = (risk) => {
    setEditingRisk(risk);
    setModalOpen(true);
  };

  const handleSaveRisk = async (values) => {
    try {
      if (editingRisk) {
        // Update existing risk
        const updatedRisk = { ...editingRisk, ...values };
        setRisks(prev => prev.map(r => r.id === editingRisk.id ? updatedRisk : r));
        showNotification('Risk updated successfully', 'success');
      } else {
        // Add new risk
        const newRisk = {
          id: Date.now(),
          ...values,
          riskScore: Math.round((values.probability * values.impact) / 100),
          status: 'Active',
          lastAssessment: new Date().toISOString().split('T')[0],
          trend: 'stable',
        };
        setRisks(prev => [...prev, newRisk]);
        showNotification('Risk created successfully', 'success');
      }
      setModalOpen(false);
    } catch (error) {
      showNotification('Failed to save risk', 'error');
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      High: 'error',
      Medium: 'warning',
      Low: 'success',
    };
    return colors[severity] || 'default';
  };

  const getStatusColor = (status) => {
    const colors = {
      Active: 'error',
      Mitigated: 'success',
      Monitored: 'info',
      Closed: 'default',
    };
    return colors[status] || 'default';
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUpIcon color="error" />;
      case 'decreasing':
        return <TrendingDownIcon color="success" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  // Form fields configuration
  const formFields = [
    {
      name: 'title',
      label: 'Risk Title',
      type: 'text',
      required: 'Risk title is required',
      gridProps: { xs: 12 },
    },
    {
      name: 'description',
      label: 'Risk Description',
      type: 'textarea',
      required: 'Risk description is required',
      gridProps: { xs: 12 },
    },
    {
      name: 'category',
      label: 'Category',
      type: 'select',
      required: 'Category is required',
      options: [
        { value: 'Financial', label: 'Financial' },
        { value: 'Operational', label: 'Operational' },
        { value: 'Environmental', label: 'Environmental' },
        { value: 'Compliance', label: 'Compliance' },
        { value: 'Technical', label: 'Technical' },
        { value: 'Safety', label: 'Safety' },
        { value: 'Supply Chain', label: 'Supply Chain' },
      ],
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'project',
      label: 'Project',
      type: 'select',
      required: 'Project is required',
      options: [
        { value: 'Downtown Office Complex', label: 'Downtown Office Complex' },
        { value: 'Healthcare Facility', label: 'Healthcare Facility' },
        { value: 'Infrastructure Project', label: 'Infrastructure Project' },
        { value: 'Industrial Plant', label: 'Industrial Plant' },
        { value: 'All Projects', label: 'All Projects' },
      ],
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'severity',
      label: 'Severity',
      type: 'select',
      required: 'Severity is required',
      options: [
        { value: 'High', label: 'High' },
        { value: 'Medium', label: 'Medium' },
        { value: 'Low', label: 'Low' },
      ],
      gridProps: { xs: 12, md: 4 },
    },
    {
      name: 'probability',
      label: 'Probability (%)',
      type: 'number',
      required: 'Probability is required',
      min: 1,
      max: 100,
      gridProps: { xs: 12, md: 4 },
    },
    {
      name: 'impact',
      label: 'Impact (%)',
      type: 'number',
      required: 'Impact is required',
      min: 1,
      max: 100,
      gridProps: { xs: 12, md: 4 },
    },
    {
      name: 'mitigation',
      label: 'Mitigation Strategy',
      type: 'textarea',
      required: 'Mitigation strategy is required',
      gridProps: { xs: 12 },
    },
    {
      name: 'owner',
      label: 'Risk Owner',
      type: 'text',
      required: 'Risk owner is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'dueDate',
      label: 'Due Date',
      type: 'date',
      required: 'Due date is required',
      gridProps: { xs: 12, md: 6 },
    },
  ];

  // Risk summary data for charts
  const riskSummaryData = [
    { name: 'High', value: risks.filter(r => r.severity === 'High').length, color: '#f44336' },
    { name: 'Medium', value: risks.filter(r => r.severity === 'Medium').length, color: '#ff9800' },
    { name: 'Low', value: risks.filter(r => r.severity === 'Low').length, color: '#4caf50' },
  ];

  const categoryData = [
    { name: 'Financial', value: risks.filter(r => r.category === 'Financial').length },
    { name: 'Operational', value: risks.filter(r => r.category === 'Operational').length },
    { name: 'Environmental', value: risks.filter(r => r.category === 'Environmental').length },
    { name: 'Compliance', value: risks.filter(r => r.category === 'Compliance').length },
    { name: 'Technical', value: risks.filter(r => r.category === 'Technical').length },
  ];

  const statusData = [
    { name: 'Active', value: risks.filter(r => r.status === 'Active').length },
    { name: 'Mitigated', value: risks.filter(r => r.status === 'Mitigated').length },
    { name: 'Monitored', value: risks.filter(r => r.status === 'Monitored').length },
  ];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Risk Analysis
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setModalOpen(true)}
        >
          Add Risk
        </Button>
      </Box>

      {/* ML Insights Section */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <MLInsights
            type="risk"
            title="AI Risk Intelligence"
            showRefresh={true}
            onRefresh={() => dispatch(fetchRiskAnalysisInsights())}
          />
        </Grid>
      </Grid>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Risks
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {risks.length}
                  </Typography>
                </Box>
                <AssessmentIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    High Risk
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="error.main">
                    {risks.filter(r => r.severity === 'High').length}
                  </Typography>
                </Box>
                <WarningIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Mitigated
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="success.main">
                    {risks.filter(r => r.status === 'Mitigated').length}
                  </Typography>
                </Box>
                <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Avg Risk Score
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="warning.main">
                    {Math.round(risks.reduce((sum, r) => sum + r.riskScore, 0) / risks.length)}
                  </Typography>
                </Box>
                <ErrorIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Risk Alerts */}
      <Alert severity="warning" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Risk Alert:</strong> 2 high-severity risks require immediate attention. 
          Review mitigation strategies and assign action items to risk owners.
        </Typography>
      </Alert>

      {/* Tabs for different views */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Risk Overview" />
          <Tab label="Risk Matrix" />
          <Tab label="Mitigation Status" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Risk Distribution Chart */}
          <Grid item xs={12} md={6}>
            <Chart
              title="Risk Distribution by Severity"
              data={riskSummaryData}
              type="pie"
              height={300}
            />
          </Grid>

          {/* Category Distribution Chart */}
          <Grid item xs={12} md={6}>
            <Chart
              title="Risks by Category"
              data={categoryData}
              type="bar"
              height={300}
            />
          </Grid>

          {/* Risk List */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Active Risks
                </Typography>
                <Box>
                  {risks.filter(r => r.status === 'Active').map((risk) => (
                    <Box key={risk.id} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                        <Box>
                          <Typography variant="subtitle1" fontWeight="medium">
                            {risk.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {risk.description}
                          </Typography>
                        </Box>
                        <Box display="flex" gap={1}>
                          <Chip
                            label={risk.severity}
                            color={getSeverityColor(risk.severity)}
                            size="small"
                          />
                          <Chip
                            label={risk.category}
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      </Box>
                      
                      <Box display="flex" gap={2} mb={1}>
                        <Typography variant="caption">
                          <strong>Probability:</strong> {risk.probability}%
                        </Typography>
                        <Typography variant="caption">
                          <strong>Impact:</strong> {risk.impact}%
                        </Typography>
                        <Typography variant="caption">
                          <strong>Risk Score:</strong> {risk.riskScore}
                        </Typography>
                      </Box>

                      <Box display="flex" gap={2} mb={1}>
                        <Typography variant="caption">
                          <strong>Owner:</strong> {risk.owner}
                        </Typography>
                        <Typography variant="caption">
                          <strong>Due:</strong> {risk.dueDate}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={0.5}>
                          <Typography variant="caption">
                            <strong>Trend:</strong>
                          </Typography>
                          {getTrendIcon(risk.trend)}
                        </Box>
                      </Box>

                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleEditRisk(risk)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="success"
                        >
                          Mark Mitigated
                        </Button>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          {/* Risk Matrix Chart */}
          <Grid item xs={12}>
            <Chart
              title="Risk Matrix - Probability vs Impact"
              data={risks.map(r => ({
                name: r.title,
                probability: r.probability,
                impact: r.impact,
                severity: r.severity,
                category: r.category,
              }))}
              type="scatter"
              height={400}
            />
          </Grid>

          {/* Risk Status Chart */}
          <Grid item xs={12} md={6}>
            <Chart
              title="Risk Status Distribution"
              data={statusData}
              type="pie"
              height={300}
            />
          </Grid>

          {/* Risk Trend Analysis */}
          <Grid item xs={12} md={6}>
            <Chart
              title="Risk Trend Analysis"
              data={[
                { name: 'Week 1', high: 3, medium: 2, low: 1 },
                { name: 'Week 2', high: 2, medium: 3, low: 2 },
                { name: 'Week 3', high: 2, medium: 2, low: 3 },
                { name: 'Week 4', high: 1, medium: 3, low: 4 },
              ]}
              type="line"
              height={300}
            />
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          {/* Mitigation Progress */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Mitigation Progress
                </Typography>
                {risks.map((risk) => (
                  <Box key={risk.id} sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="subtitle2">
                        {risk.title}
                      </Typography>
                      <Chip
                        label={risk.status}
                        color={getStatusColor(risk.status)}
                        size="small"
                      />
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={risk.status === 'Mitigated' ? 100 : risk.status === 'Monitored' ? 75 : 25}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {risk.mitigation}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Add/Edit Risk Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingRisk ? 'Edit Risk' : 'Add New Risk'}
        maxWidth="md"
        fullWidth
      >
        <Form
          fields={formFields}
          initialValues={editingRisk || {}}
          onSubmit={handleSaveRisk}
          onCancel={() => setModalOpen(false)}
          submitText={editingRisk ? 'Update Risk' : 'Create Risk'}
          cancelText="Cancel"
        />
      </Modal>

      {/* Notification */}
      <Notification
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={() => setNotification({ ...notification, open: false })}
      />
    </Box>
  );
};

export default RiskAnalysis;
