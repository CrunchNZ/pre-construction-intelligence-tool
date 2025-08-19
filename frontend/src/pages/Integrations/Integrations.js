import React, { useState, useEffect } from 'react';
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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  FormControlLabel,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Sync as SyncIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  Business as BusinessIcon,
  Cloud as CloudIcon,
  Storage as StorageIcon,
  Api as ApiIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';

const Integrations = () => {
  const [loading, setLoading] = useState(false);
  const [integrations, setIntegrations] = useState([]);
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Mock data for demonstration - replace with actual API calls
  const mockIntegrations = [
    {
      id: 'procore',
      name: 'Procore',
      type: 'Construction Management',
      status: 'connected',
      lastSync: '2024-01-15T10:30:00Z',
      syncStatus: 'success',
      config: {
        apiKey: '***',
        baseUrl: 'https://api.procore.com',
        projectId: '12345',
        syncInterval: 15,
      },
      metrics: {
        projectsSynced: 45,
        lastSyncDuration: '2.3s',
        errorRate: 0.02,
        dataVolume: '2.1GB',
      },
      description: 'Leading construction project management platform',
      icon: <BusinessIcon />,
    },
    {
      id: 'jobpac',
      name: 'Jobpac',
      type: 'Project Management',
      status: 'connected',
      lastSync: '2024-01-15T09:45:00Z',
      syncStatus: 'success',
      config: {
        apiKey: '***',
        baseUrl: 'https://api.jobpac.com',
        companyId: '67890',
        syncInterval: 30,
      },
      metrics: {
        projectsSynced: 23,
        lastSyncDuration: '1.8s',
        errorRate: 0.01,
        dataVolume: '1.2GB',
      },
      description: 'Australian construction project management system',
      icon: <BusinessIcon />,
    },
    {
      id: 'greentree',
      name: 'Greentree',
      type: 'ERP System',
      status: 'connected',
      lastSync: '2024-01-15T08:15:00Z',
      syncStatus: 'success',
      config: {
        apiKey: '***',
        baseUrl: 'https://api.greentree.com',
        databaseId: 'DB001',
        syncInterval: 60,
      },
      metrics: {
        projectsSynced: 67,
        lastSyncDuration: '3.1s',
        errorRate: 0.03,
        dataVolume: '3.8GB',
      },
      description: 'Enterprise resource planning for construction',
      icon: <StorageIcon />,
    },
    {
      id: 'procurepro',
      name: 'ProcurePro',
      type: 'Procurement',
      status: 'connected',
      lastSync: '2024-01-15T11:00:00Z',
      syncStatus: 'success',
      config: {
        apiKey: '***',
        baseUrl: 'https://api.procurepro.com',
        organizationId: 'ORG123',
        syncInterval: 20,
      },
      metrics: {
        projectsSynced: 34,
        lastSyncDuration: '1.5s',
        errorRate: 0.01,
        dataVolume: '1.9GB',
      },
      description: 'Construction procurement and supply chain management',
      icon: <CloudIcon />,
    },
    {
      id: 'bim',
      name: 'BIM Integration',
      type: '3D Modeling',
      status: 'connected',
      lastSync: '2024-01-15T07:30:00Z',
      syncStatus: 'success',
      config: {
        apiKey: '***',
        baseUrl: 'https://api.bim.com',
        modelServer: 'bim-server-01',
        syncInterval: 120,
      },
      metrics: {
        modelsSynced: 12,
        lastSyncDuration: '45.2s',
        errorRate: 0.05,
        dataVolume: '15.7GB',
      },
      description: 'Building Information Modeling integration',
      icon: <ApiIcon />,
    },
  ];

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setIntegrations(mockIntegrations);
    } catch (error) {
      console.error('Failed to load integrations:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load integrations',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      connected: 'success',
      connecting: 'warning',
      disconnected: 'error',
      error: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircleIcon color="success" />;
      case 'connecting':
        return <CircularProgress size={20} />;
      case 'disconnected':
        return <ErrorIcon color="error" />;
      case 'error':
        return <WarningIcon color="warning" />;
      default:
        return <ErrorIcon color="error" />;
    }
  };

  const getSyncStatusColor = (status) => {
    const colors = {
      success: 'success',
      warning: 'warning',
      error: 'error',
      pending: 'info',
    };
    return colors[status] || 'default';
  };

  const handleTestConnection = async (integration) => {
    setSelectedIntegration(integration);
    setTestDialogOpen(true);
  };

  const handleConfigure = (integration) => {
    setSelectedIntegration(integration);
    setConfigDialogOpen(true);
  };

  const handleSync = async (integration) => {
    try {
      setLoading(true);
      // Simulate sync operation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update integration status
      setIntegrations(prev => prev.map(int => 
        int.id === integration.id 
          ? { ...int, lastSync: new Date().toISOString(), syncStatus: 'success' }
          : int
      ));
      
      setSnackbar({
        open: true,
        message: `${integration.name} sync completed successfully`,
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Failed to sync ${integration.name}`,
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleIntegration = async (integration) => {
    try {
      const newStatus = integration.status === 'connected' ? 'disconnected' : 'connected';
      
      setIntegrations(prev => prev.map(int => 
        int.id === integration.id 
          ? { ...int, status: newStatus }
          : int
      ));
      
      setSnackbar({
        open: true,
        message: `${integration.name} ${newStatus === 'connected' ? 'connected' : 'disconnected'}`,
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Failed to toggle ${integration.name}`,
        severity: 'error',
      });
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds) => {
    return `${seconds}s`;
  };

  const formatDataVolume = (bytes) => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)}GB`;
  };

  if (loading && integrations.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" gutterBottom>
          Integrations
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage connections to external construction management systems and monitor data synchronization
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Integrations
              </Typography>
              <Typography variant="h4">
                {integrations.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Connected
              </Typography>
              <Typography variant="h4" color="success.main">
                {integrations.filter(i => i.status === 'connected').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Last Sync
              </Typography>
              <Typography variant="h6">
                {integrations.length > 0 ? formatDate(integrations[0].lastSync) : 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Data
              </Typography>
              <Typography variant="h6">
                {integrations.reduce((total, int) => {
                  const volume = parseFloat(int.metrics.dataVolume.replace('GB', ''));
                  return total + volume;
                }, 0).toFixed(1)}GB
              </Typography>
            </CardContent>
          </Card>
      </Grid>

      {/* Integrations List */}
      <Grid container spacing={3}>
        {integrations.map((integration) => (
          <Grid item xs={12} key={integration.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Box display="flex" alignItems="center" gap={2}>
                    {integration.icon}
                    <Box>
                      <Typography variant="h6">
                        {integration.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {integration.description}
                      </Typography>
                    </Box>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip
                      label={integration.type}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      icon={getStatusIcon(integration.status)}
                      label={integration.status}
                      color={getStatusColor(integration.status)}
                      size="small"
                    />
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Metrics Row */}
                <Grid container spacing={2} mb={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Projects/Models
                    </Typography>
                    <Typography variant="h6">
                      {integration.metrics.projectsSynced}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Last Sync
                    </Typography>
                    <Typography variant="body2">
                      {formatDate(integration.lastSync)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Sync Duration
                    </Typography>
                    <Typography variant="body2">
                      {formatDuration(integration.metrics.lastSyncDuration)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Data Volume
                    </Typography>
                    <Typography variant="body2">
                      {integration.metrics.dataVolume}
                    </Typography>
                  </Grid>
                </Grid>

                {/* Actions Row */}
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center" gap={1}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={integration.status === 'connected'}
                          onChange={() => handleToggleIntegration(integration)}
                          color="primary"
                        />
                      }
                      label="Active"
                    />
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Tooltip title="Test Connection">
                      <IconButton
                        onClick={() => handleTestConnection(integration)}
                        size="small"
                      >
                        <PlayIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Sync Now">
                      <IconButton
                        onClick={() => handleSync(integration)}
                        size="small"
                        disabled={loading}
                      >
                        <SyncIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Configure">
                      <IconButton
                        onClick={() => handleConfigure(integration)}
                        size="small"
                      >
                        <SettingsIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Configuration Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Configure {selectedIntegration?.name}
        </DialogTitle>
        <DialogContent>
          {selectedIntegration && (
            <Box mt={2}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="API Key"
                    value={selectedIntegration.config.apiKey}
                    type="password"
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Base URL"
                    value={selectedIntegration.config.baseUrl}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Project/Company ID"
                    value={selectedIntegration.config.projectId || selectedIntegration.config.companyId || selectedIntegration.config.databaseId || selectedIntegration.config.organizationId}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Sync Interval (minutes)</InputLabel>
                    <Select
                      value={selectedIntegration.config.syncInterval}
                      label="Sync Interval (minutes)"
                    >
                      <MenuItem value={5}>5 minutes</MenuItem>
                      <MenuItem value={15}>15 minutes</MenuItem>
                      <MenuItem value={30}>30 minutes</MenuItem>
                      <MenuItem value={60}>1 hour</MenuItem>
                      <MenuItem value={120}>2 hours</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" onClick={() => setConfigDialogOpen(false)}>
            Save Configuration
          </Button>
        </DialogActions>
      </Dialog>

      {/* Test Connection Dialog */}
      <Dialog
        open={testDialogOpen}
        onClose={() => setTestDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Test Connection - {selectedIntegration?.name}
        </DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <Typography variant="body1" gutterBottom>
              Testing connection to {selectedIntegration?.name}...
            </Typography>
            <Box display="flex" alignItems="center" gap={2} mt={2}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                Verifying API credentials and connectivity
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Integrations;
