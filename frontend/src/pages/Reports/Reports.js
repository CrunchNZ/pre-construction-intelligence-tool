import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Add as AddIcon,
  Download as DownloadIcon,
  Email as EmailIcon,
  Schedule as ScheduleIcon,
  History as HistoryIcon,
  Description as DescriptionIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  Engineering as EngineeringIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { Chart, Modal, Form, Notification } from '../../components/common';
import MLInsights from '../../components/common/MLInsights';
import { fetchReportsInsights } from '../../store/slices/mlInsightsSlice';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [reportType, setReportType] = useState('comprehensive');
  const dispatch = useDispatch();

  // Mock data - replace with actual API calls
  const mockReports = [
    {
      id: 1,
      name: 'Monthly Project Summary',
      type: 'Project Summary',
      status: 'Completed',
      generatedAt: '2024-01-15 10:30',
      generatedBy: 'John Smith',
      format: 'PDF',
      size: '2.4 MB',
      downloadUrl: '#',
      schedule: 'Monthly',
      lastScheduled: '2024-01-15',
      nextScheduled: '2024-02-15',
    },
    {
      id: 2,
      name: 'Q4 Financial Analysis',
      type: 'Financial',
      status: 'Completed',
      generatedAt: '2024-01-10 14:20',
      generatedBy: 'Sarah Johnson',
      format: 'Excel',
      size: '1.8 MB',
      downloadUrl: '#',
      schedule: 'Quarterly',
      lastScheduled: '2024-01-10',
      nextScheduled: '2024-04-10',
    },
    {
      id: 3,
      name: 'Risk Assessment Report',
      type: 'Risk Analysis',
      status: 'In Progress',
      generatedAt: '2024-01-12 09:15',
      generatedBy: 'Mike Davis',
      format: 'PDF',
      size: '3.1 MB',
      downloadUrl: '#',
      schedule: 'Weekly',
      lastScheduled: '2024-01-12',
      nextScheduled: '2024-01-19',
    },
    {
      id: 4,
      name: 'Supplier Performance Review',
      type: 'Supplier Analysis',
      status: 'Completed',
      generatedAt: '2024-01-08 16:45',
      generatedBy: 'Lisa Chen',
      format: 'PDF',
      size: '1.5 MB',
      downloadUrl: '#',
      schedule: 'Monthly',
      lastScheduled: '2024-01-08',
      nextScheduled: '2024-02-08',
    },
  ];

  const mockTemplates = [
    {
      id: 1,
      name: 'Project Summary Report',
      description: 'Comprehensive overview of project status, milestones, and key metrics',
      category: 'Project Management',
      frequency: 'Monthly',
      estimatedTime: '5-10 minutes',
      parameters: ['Project Selection', 'Date Range', 'Include Charts', 'Include Budget'],
      lastUsed: '2024-01-15',
      usageCount: 24,
    },
    {
      id: 2,
      name: 'Financial Performance Report',
      description: 'Detailed financial analysis including costs, budgets, and profitability',
      category: 'Financial',
      frequency: 'Monthly',
      estimatedTime: '10-15 minutes',
      parameters: ['Project Selection', 'Date Range', 'Cost Categories', 'Budget Comparison'],
      lastUsed: '2024-01-10',
      usageCount: 18,
    },
    {
      id: 3,
      name: 'Risk Assessment Report',
      description: 'Comprehensive risk analysis with mitigation strategies and trends',
      category: 'Risk Management',
      frequency: 'Weekly',
      estimatedTime: '8-12 minutes',
      parameters: ['Risk Categories', 'Severity Levels', 'Include Mitigation', 'Trend Analysis'],
      lastUsed: '2024-01-12',
      usageCount: 32,
    },
    {
      id: 4,
      name: 'Supplier Performance Report',
      description: 'Supplier evaluation and performance metrics analysis',
      category: 'Supplier Management',
      frequency: 'Monthly',
      estimatedTime: '6-10 minutes',
      parameters: ['Supplier Selection', 'Performance Metrics', 'Rating Thresholds', 'Historical Data'],
      lastUsed: '2024-01-08',
      usageCount: 15,
    },
    {
      id: 5,
      name: 'Executive Dashboard Report',
      description: 'High-level summary for executive stakeholders',
      category: 'Executive',
      frequency: 'Weekly',
      estimatedTime: '3-5 minutes',
      parameters: ['KPIs', 'Project Highlights', 'Risk Summary', 'Financial Overview'],
      lastUsed: '2024-01-14',
      usageCount: 28,
    },
  ];

  useEffect(() => {
    loadData();
    loadTemplates();
    // Load ML insights
    dispatch(fetchReportsInsights(reportType));
  }, [dispatch, reportType]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setReports(mockReports);
      setTemplates(mockTemplates);
    } catch (error) {
      showNotification('Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    // Simulate API call for templates
    await new Promise(resolve => setTimeout(resolve, 1000));
    setTemplates(mockTemplates);
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleGenerateReport = (template) => {
    setSelectedTemplate(template);
    setModalOpen(true);
  };

  const handleGenerateReportSubmit = async (values) => {
    setGenerating(true);
    try {
      // Simulate report generation
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const newReport = {
        id: Date.now(),
        name: values.reportName || selectedTemplate.name,
        type: selectedTemplate.category,
        status: 'Completed',
        generatedAt: new Date().toLocaleString(),
        generatedBy: 'Current User',
        format: values.format || 'PDF',
        size: `${(Math.random() * 3 + 1).toFixed(1)} MB`,
        downloadUrl: '#',
        schedule: values.schedule || 'One-time',
        lastScheduled: new Date().toISOString().split('T')[0],
        nextScheduled: values.schedule === 'One-time' ? null : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      };
      
      setReports(prev => [newReport, ...prev]);
      showNotification('Report generated successfully', 'success');
      setModalOpen(false);
    } catch (error) {
      showNotification('Failed to generate report', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = (report) => {
    // Simulate download
    showNotification(`Downloading ${report.name}...`, 'info');
  };

  const handleScheduleReport = (report) => {
    showNotification(`Scheduling ${report.name}...`, 'info');
  };

  const getStatusColor = (status) => {
    const colors = {
      Completed: 'success',
      'In Progress': 'warning',
      Failed: 'error',
      Pending: 'info',
    };
    return colors[status] || 'default';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'Project Management': <EngineeringIcon />,
      'Financial': <TrendingUpIcon />,
      'Risk Management': <AssessmentIcon />,
      'Supplier Management': <BusinessIcon />,
      'Executive': <DescriptionIcon />,
    };
    return icons[category] || <DescriptionIcon />;
  };

  // Report generation form fields
  const getReportFormFields = () => {
    if (!selectedTemplate) return [];
    
    const baseFields = [
      {
        name: 'reportName',
        label: 'Report Name',
        type: 'text',
        defaultValue: selectedTemplate.name,
        gridProps: { xs: 12 },
      },
      {
        name: 'format',
        label: 'Output Format',
        type: 'select',
        defaultValue: 'PDF',
        options: [
          { value: 'PDF', label: 'PDF Document' },
          { value: 'Excel', label: 'Excel Spreadsheet' },
          { value: 'Word', label: 'Word Document' },
          { value: 'PowerPoint', label: 'PowerPoint Presentation' },
        ],
        gridProps: { xs: 12, md: 6 },
      },
      {
        name: 'schedule',
        label: 'Schedule',
        type: 'select',
        defaultValue: 'One-time',
        options: [
          { value: 'One-time', label: 'One-time Generation' },
          { value: 'Daily', label: 'Daily' },
          { value: 'Weekly', label: 'Weekly' },
          { value: 'Monthly', label: 'Monthly' },
          { value: 'Quarterly', label: 'Quarterly' },
        ],
        gridProps: { xs: 12, md: 6 },
      },
    ];

    // Add template-specific parameters
    const parameterFields = selectedTemplate.parameters.map(param => ({
      name: `param_${param.toLowerCase().replace(/\s+/g, '_')}`,
      label: param,
      type: 'text',
      gridProps: { xs: 12, md: 6 },
    }));

    return [...baseFields, ...parameterFields];
  };

  // Report statistics for charts
  const reportTypeData = [
    { name: 'Project Management', value: reports.filter(r => r.type === 'Project Management').length },
    { name: 'Financial', value: reports.filter(r => r.type === 'Financial').length },
    { name: 'Risk Analysis', value: reports.filter(r => r.type === 'Risk Analysis').length },
    { name: 'Supplier Analysis', value: reports.filter(r => r.type === 'Supplier Analysis').length },
  ];

  const reportStatusData = [
    { name: 'Completed', value: reports.filter(r => r.status === 'Completed').length },
    { name: 'In Progress', value: reports.filter(r => r.status === 'In Progress').length },
    { name: 'Failed', value: reports.filter(r => r.status === 'Failed').length },
  ];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Reports
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setModalOpen(true)}
        >
          Generate Report
        </Button>
      </Box>

      {/* ML Insights Section */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <MLInsights
            type="reports"
            reportType={reportType}
            title="AI Report Intelligence"
            showRefresh={true}
            onRefresh={() => dispatch(fetchReportsInsights(reportType))}
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
                    Total Reports
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {reports.length}
                  </Typography>
                </Box>
                <DescriptionIcon color="primary" sx={{ fontSize: 40 }} />
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
                    Templates
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="info.main">
                    {templates.length}
                  </Typography>
                </Box>
                <AssessmentIcon color="info" sx={{ fontSize: 40 }} />
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
                    Scheduled
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="warning.main">
                    {reports.filter(r => r.schedule !== 'One-time').length}
                  </Typography>
                </Box>
                <ScheduleIcon color="warning" sx={{ fontSize: 40 }} />
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
                    This Month
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="success.main">
                    {reports.filter(r => {
                      const reportDate = new Date(r.generatedAt);
                      const now = new Date();
                      return reportDate.getMonth() === now.getMonth() && reportDate.getFullYear() === now.getFullYear();
                    }).length}
                  </Typography>
                </Box>
                <HistoryIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Report Generation Progress */}
      {generating && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="body2">
              <strong>Generating Report:</strong> Please wait while we process your request...
            </Typography>
            <LinearProgress sx={{ flexGrow: 1 }} />
          </Box>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Report Templates */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Report Templates
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Choose from pre-configured templates to quickly generate reports
              </Typography>
              
              <List>
                {templates.map((template) => (
                  <ListItem key={template.id} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, mb: 1 }}>
                    <ListItemIcon>
                      {getCategoryIcon(template.category)}
                    </ListItemIcon>
                    <ListItemText
                      primary={template.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {template.description}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip label={template.category} size="small" variant="outlined" />
                            <Chip label={template.frequency} size="small" variant="outlined" />
                            <Chip label={`~${template.estimatedTime}`} size="small" variant="outlined" />
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Button
                        size="small"
                        variant="contained"
                        onClick={() => handleGenerateReport(template)}
                      >
                        Generate
                      </Button>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Reports */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Reports
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Your recently generated and scheduled reports
              </Typography>
              
              <List>
                {reports.slice(0, 5).map((report) => (
                  <ListItem key={report.id} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, mb: 1 }}>
                    <ListItemIcon>
                      <DescriptionIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={report.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Generated by {report.generatedBy} on {report.generatedAt}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip label={report.type} size="small" variant="outlined" />
                            <Chip label={report.format} size="small" variant="outlined" />
                            <Chip label={report.status} size="small" color={getStatusColor(report.status)} />
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownloadReport(report)}
                        >
                          Download
                        </Button>
                        {report.schedule !== 'One-time' && (
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<ScheduleIcon />}
                            onClick={() => handleScheduleReport(report)}
                          >
                            Schedule
                          </Button>
                        )}
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Report Analytics */}
        <Grid item xs={12} md={6}>
          <Chart
            title="Reports by Type"
            data={reportTypeData}
            type="pie"
            height={300}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Chart
            title="Report Status Distribution"
            data={reportStatusData}
            type="bar"
            height={300}
          />
        </Grid>
      </Grid>

      {/* Report Generation Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={selectedTemplate ? `Generate ${selectedTemplate.name}` : 'Generate Report'}
        maxWidth="md"
        fullWidth
      >
        {selectedTemplate ? (
          <Form
            fields={getReportFormFields()}
            onSubmit={handleGenerateReportSubmit}
            onCancel={() => setModalOpen(false)}
            submitText="Generate Report"
            cancelText="Cancel"
            loading={generating}
          />
        ) : (
          <Box p={3}>
            <Typography variant="body1" color="text.secondary" textAlign="center">
              Please select a report template to continue
            </Typography>
          </Box>
        )}
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

export default Reports;
