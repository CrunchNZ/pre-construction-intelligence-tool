import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
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
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Fab
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as TrainIcon,
  CloudUpload as DeployIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import { DataTable } from '../../components/common/DataTable';
import { Modal } from '../../components/common/Modal';
import { Notification } from '../../components/common/Notification';
import { Chart } from '../../components/common/Chart';

const AIModels = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [trainingModalOpen, setTrainingModalOpen] = useState(false);
  const [performanceModalOpen, setPerformanceModalOpen] = useState(false);

  // Form states
  const [formData, setFormData] = useState({
    name: '',
    model_type: '',
    version: '1.0.0',
    description: '',
    algorithm: '',
    hyperparameters: {},
    feature_columns: [],
    target_column: ''
  });

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai_models/models/');
      if (response.ok) {
        const data = await response.json();
        setModels(data);
      } else {
        throw new Error('Failed to fetch models');
      }
    } catch (error) {
      console.error('Error fetching models:', error);
      setNotification({
        open: true,
        message: 'Failed to fetch models',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateModel = async () => {
    try {
      const response = await fetch('/api/ai_models/models/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setNotification({
          open: true,
          message: 'Model created successfully',
          severity: 'success'
        });
        setCreateModalOpen(false);
        resetForm();
        fetchModels();
      } else {
        throw new Error('Failed to create model');
      }
    } catch (error) {
      console.error('Error creating model:', error);
      setNotification({
        open: true,
        message: 'Failed to create model',
        severity: 'error'
      });
    }
  };

  const handleTrainModel = async (modelId) => {
    try {
      const response = await fetch(`/api/ai_models/models/${modelId}/train/`, {
        method: 'POST',
      });

      if (response.ok) {
        setNotification({
          open: true,
          message: 'Training started successfully',
          severity: 'success'
        });
        fetchModels();
      } else {
        throw new Error('Failed to start training');
      }
    } catch (error) {
      console.error('Error starting training:', error);
      setNotification({
        open: true,
        message: 'Failed to start training',
        severity: 'error'
      });
    }
  };

  const handleDeployModel = async (modelId) => {
    try {
      const response = await fetch(`/api/ai_models/models/${modelId}/deploy/`, {
        method: 'POST',
      });

      if (response.ok) {
        setNotification({
          open: true,
          message: 'Model deployed successfully',
          severity: 'success'
        });
        fetchModels();
      } else {
        throw new Error('Failed to deploy model');
      }
    } catch (error) {
      console.error('Error deploying model:', error);
      setNotification({
        open: true,
        message: 'Failed to deploy model',
        severity: 'error'
      });
    }
  };

  const handleDeleteModel = async (modelId) => {
    if (window.confirm('Are you sure you want to delete this model?')) {
      try {
        const response = await fetch(`/api/ai_models/models/${modelId}/`, {
          method: 'DELETE',
        });

        if (response.ok) {
          setNotification({
            open: true,
            message: 'Model deleted successfully',
            severity: 'success'
          });
          fetchModels();
        } else {
          throw new Error('Failed to delete model');
        }
      } catch (error) {
        console.error('Error deleting model:', error);
        setNotification({
          open: true,
          message: 'Failed to delete model',
          severity: 'error'
        });
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      model_type: '',
      version: '1.0.0',
      description: '',
      algorithm: '',
      hyperparameters: {},
      feature_columns: [],
      target_column: ''
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'training':
        return 'warning';
      case 'failed':
        return 'error';
      case 'draft':
        return 'default';
      case 'deprecated':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getModelTypeDisplay = (type) => {
    const typeMap = {
      'cost_prediction': 'Cost Prediction',
      'timeline_prediction': 'Timeline Prediction',
      'risk_assessment': 'Risk Assessment',
      'quality_prediction': 'Quality Prediction',
      'safety_prediction': 'Safety Prediction',
      'change_order_impact': 'Change Order Impact'
    };
    return typeMap[type] || type;
  };

  const columns = [
    {
      field: 'name',
      headerName: 'Model Name',
      width: 200,
      renderCell: (params) => (
        <Typography variant="subtitle2" fontWeight="bold">
          {params.value}
        </Typography>
      )
    },
    {
      field: 'model_type',
      headerName: 'Type',
      width: 150,
      renderCell: (params) => (
        <Chip
          label={getModelTypeDisplay(params.value)}
          size="small"
          color="primary"
          variant="outlined"
        />
      )
    },
    {
      field: 'algorithm',
      headerName: 'Algorithm',
      width: 150
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color={getStatusColor(params.value)}
        />
      )
    },
    {
      field: 'accuracy',
      headerName: 'Accuracy',
      width: 120,
      renderCell: (params) => (
        params.value ? `${(params.value * 100).toFixed(1)}%` : 'N/A'
      )
    },
    {
      field: 'last_trained',
      headerName: 'Last Trained',
      width: 150,
      renderCell: (params) => (
        params.value ? new Date(params.value).toLocaleDateString() : 'Never'
      )
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={() => handleViewModel(params.row)}
            >
              <ViewIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit Model">
            <IconButton
              size="small"
              onClick={() => handleEditModel(params.row)}
            >
              <EditIcon />
            </IconButton>
          </Tooltip>
          {params.row.status === 'draft' && (
            <Tooltip title="Train Model">
              <IconButton
                size="small"
                color="primary"
                onClick={() => handleTrainModel(params.row.id)}
              >
                <TrainIcon />
              </IconButton>
            </Tooltip>
          )}
          {params.row.status === 'active' && (
            <Tooltip title="Deploy Model">
              <IconButton
                size="small"
                color="success"
                onClick={() => handleDeployModel(params.row.id)}
              >
                <DeployIcon />
              </IconButton>
            </Tooltip>
          )}
          <Tooltip title="Delete Model">
            <IconButton
              size="small"
              color="error"
              onClick={() => handleDeleteModel(params.row.id)}
            >
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  const handleViewModel = (model) => {
    setSelectedModel(model);
    setPerformanceModalOpen(true);
  };

  const handleEditModel = (model) => {
    setSelectedModel(model);
    setFormData({
      name: model.name,
      model_type: model.model_type,
      version: model.version,
      description: model.description,
      algorithm: model.algorithm,
      hyperparameters: model.hyperparameters,
      feature_columns: model.feature_columns,
      target_column: model.target_column
    });
    setEditModalOpen(true);
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const renderCreateModelForm = () => (
    <Box component="form" sx={{ mt: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Model Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth required>
            <InputLabel>Model Type</InputLabel>
            <Select
              value={formData.model_type}
              onChange={(e) => setFormData({ ...formData, model_type: e.target.value })}
              label="Model Type"
            >
              <MenuItem value="cost_prediction">Cost Prediction</MenuItem>
              <MenuItem value="timeline_prediction">Timeline Prediction</MenuItem>
              <MenuItem value="risk_assessment">Risk Assessment</MenuItem>
              <MenuItem value="quality_prediction">Quality Prediction</MenuItem>
              <MenuItem value="safety_prediction">Safety Prediction</MenuItem>
              <MenuItem value="change_order_impact">Change Order Impact</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Version"
            value={formData.version}
            onChange={(e) => setFormData({ ...formData, version: e.target.value })}
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Algorithm"
            value={formData.algorithm}
            onChange={(e) => setFormData({ ...formData, algorithm: e.target.value })}
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Feature Columns (comma-separated)"
            value={formData.feature_columns.join(', ')}
            onChange={(e) => setFormData({
              ...formData,
              feature_columns: e.target.value.split(',').map(s => s.trim()).filter(s => s)
            })}
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Target Column"
            value={formData.target_column}
            onChange={(e) => setFormData({ ...formData, target_column: e.target.value })}
            required
          />
        </Grid>
      </Grid>
    </Box>
  );

  const renderPerformanceMetrics = () => {
    if (!selectedModel) return null;

    const metrics = selectedModel.performance_summary || {};
    const chartData = {
      labels: Object.keys(metrics).map(key => key.replace('_', ' ').toUpperCase()),
      datasets: [{
        label: 'Performance Metrics',
        data: Object.values(metrics),
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    };

    return (
      <Box sx={{ mt: 2 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Information
                </Typography>
                <Typography><strong>Name:</strong> {selectedModel.name}</Typography>
                <Typography><strong>Type:</strong> {getModelTypeDisplay(selectedModel.model_type)}</Typography>
                <Typography><strong>Algorithm:</strong> {selectedModel.algorithm}</Typography>
                <Typography><strong>Status:</strong> {selectedModel.status}</Typography>
                <Typography><strong>Version:</strong> {selectedModel.version}</Typography>
                <Typography><strong>Last Trained:</strong> {selectedModel.last_trained ? new Date(selectedModel.last_trained).toLocaleDateString() : 'Never'}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                {Object.keys(metrics).length > 0 ? (
                  <Chart
                    type="bar"
                    data={chartData}
                    options={{
                      responsive: true,
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 1
                        }
                      }
                    }}
                  />
                ) : (
                  <Typography color="text.secondary">
                    No performance metrics available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          AI Models
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateModalOpen(true)}
        >
          Create Model
        </Button>
      </Box>

      <Tabs value={selectedTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="All Models" />
        <Tab label="Active Models" />
        <Tab label="Training Models" />
        <Tab label="Performance" />
      </Tabs>

      {selectedTab === 0 && (
        <DataTable
          data={models}
          columns={columns}
          loading={loading}
          pageSize={10}
          rowsPerPageOptions={[5, 10, 25]}
        />
      )}

      {selectedTab === 1 && (
        <DataTable
          data={models.filter(model => model.status === 'active')}
          columns={columns}
          loading={loading}
          pageSize={10}
          rowsPerPageOptions={[5, 10, 25]}
        />
      )}

      {selectedTab === 2 && (
        <DataTable
          data={models.filter(model => model.status === 'training')}
          columns={columns}
          loading={loading}
          pageSize={10}
          rowsPerPageOptions={[5, 10, 25]}
        />
      )}

      {selectedTab === 3 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Model Performance Overview
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Models
                  </Typography>
                  <Typography variant="h4">
                    {models.length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Active Models
                  </Typography>
                  <Typography variant="h4">
                    {models.filter(m => m.status === 'active').length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Training Models
                  </Typography>
                  <Typography variant="h4">
                    {models.filter(m => m.status === 'training').length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Create Model Modal */}
      <Modal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Create New AI Model"
        maxWidth="md"
      >
        {renderCreateModelForm()}
        <DialogActions>
          <Button onClick={() => setCreateModalOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateModel} variant="contained">
            Create Model
          </Button>
        </DialogActions>
      </Modal>

      {/* Edit Model Modal */}
      <Modal
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Edit AI Model"
        maxWidth="md"
      >
        {renderCreateModelForm()}
        <DialogActions>
          <Button onClick={() => setEditModalOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateModel} variant="contained">
            Update Model
          </Button>
        </DialogActions>
      </Modal>

      {/* Performance Modal */}
      <Modal
        open={performanceModalOpen}
        onClose={() => setPerformanceModalOpen(false)}
        title="Model Performance"
        maxWidth="lg"
      >
        {renderPerformanceMetrics()}
        <DialogActions>
          <Button onClick={() => setPerformanceModalOpen(false)}>Close</Button>
        </DialogActions>
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

export default AIModels;
