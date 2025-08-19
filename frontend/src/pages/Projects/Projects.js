import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
  Fab,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Business as BusinessIcon,
  Schedule as ScheduleIcon,
  AttachMoney as MoneyIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { DataTable, Modal, Form, Notification } from '../../components/common';
import MLInsights from '../../components/common/MLInsights';
import { fetchProjectInsights } from '../../store/slices/mlInsightsSlice';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const dispatch = useDispatch();

  // Mock data - replace with actual API calls
  const mockProjects = [
    {
      id: 1,
      name: 'Hospital Extension',
      client: 'City Medical Center',
      status: 'execution',
      type: 'healthcare',
      startDate: '2024-01-15',
      endDate: '2025-06-30',
      budget: 25000000,
      actualCost: 26500000,
      progress: 65,
      risk: 'medium',
      manager: 'John Smith',
    },
    {
      id: 2,
      name: 'Office Complex',
      client: 'TechCorp Inc.',
      status: 'bidding',
      type: 'commercial',
      startDate: '2024-03-01',
      endDate: '2025-12-31',
      budget: 18000000,
      actualCost: 0,
      progress: 0,
      risk: 'low',
      manager: 'Sarah Johnson',
    },
    {
      id: 3,
      name: 'Residential Tower',
      client: 'Urban Development Co.',
      status: 'planning',
      type: 'residential',
      startDate: '2024-06-01',
      endDate: '2026-03-31',
      budget: 32000000,
      actualCost: 0,
      progress: 0,
      risk: 'high',
      manager: 'Mike Davis',
    },
    {
      id: 4,
      name: 'Shopping Center',
      client: 'Retail Partners LLC',
      status: 'completed',
      type: 'commercial',
      startDate: '2023-03-01',
      endDate: '2024-02-28',
      budget: 15000000,
      actualCost: 14200000,
      progress: 100,
      risk: 'low',
      manager: 'Lisa Chen',
    },
  ];

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setProjects(mockProjects);
    } catch (error) {
      showNotification('Failed to load projects', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleAddProject = () => {
    setEditingProject(null);
    setModalOpen(true);
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setModalOpen(true);
  };

  const handleDeleteProject = async (project) => {
    if (window.confirm(`Are you sure you want to delete "${project.name}"?`)) {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        setProjects(prev => prev.filter(p => p.id !== project.id));
        showNotification('Project deleted successfully', 'success');
      } catch (error) {
        showNotification('Failed to delete project', 'error');
      }
    }
  };

  const handleSaveProject = async (values) => {
    try {
      if (editingProject) {
        // Update existing project
        const updatedProject = { ...editingProject, ...values };
        setProjects(prev => prev.map(p => p.id === editingProject.id ? updatedProject : p));
        showNotification('Project updated successfully', 'success');
      } else {
        // Add new project
        const newProject = {
          id: Date.now(),
          ...values,
          actualCost: 0,
          progress: 0,
        };
        setProjects(prev => [...prev, newProject]);
        showNotification('Project created successfully', 'success');
      }
      setModalOpen(false);
    } catch (error) {
      showNotification('Failed to save project', 'error');
    }
  };

  // Form fields configuration
  const formFields = [
    {
      name: 'name',
      label: 'Project Name',
      type: 'text',
      required: 'Project name is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'client',
      label: 'Client',
      type: 'text',
      required: 'Client name is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'type',
      label: 'Project Type',
      type: 'select',
      required: 'Project type is required',
      options: [
        { value: 'residential', label: 'Residential' },
        { value: 'commercial', label: 'Commercial' },
        { value: 'healthcare', label: 'Healthcare' },
        { value: 'industrial', label: 'Industrial' },
        { value: 'infrastructure', label: 'Infrastructure' },
      ],
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      required: 'Status is required',
      options: [
        { value: 'planning', label: 'Planning' },
        { value: 'bidding', label: 'Bidding' },
        { value: 'execution', label: 'Execution' },
        { value: 'completed', label: 'Completed' },
        { value: 'cancelled', label: 'Cancelled' },
      ],
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'startDate',
      label: 'Start Date',
      type: 'date',
      required: 'Start date is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'endDate',
      label: 'End Date',
      type: 'date',
      required: 'End date is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'budget',
      label: 'Budget ($)',
      type: 'number',
      required: 'Budget is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'manager',
      label: 'Project Manager',
      type: 'text',
      required: 'Project manager is required',
      gridProps: { xs: 12, md: 6 },
    },
  ];

  // Table columns configuration
  const columns = [
    {
      field: 'name',
      header: 'Project Name',
      render: (value, row) => (
        <Box>
          <Typography variant="subtitle2" fontWeight="medium">
            {value}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {row.client}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'status',
      header: 'Status',
      type: 'status',
    },
    {
      field: 'type',
      header: 'Type',
      type: 'chip',
      chipColor: 'default',
    },
    {
      field: 'progress',
      header: 'Progress',
      render: (value) => (
        <Box display="flex" alignItems="center" gap={1}>
          <Box
            sx={{
              width: 60,
              height: 8,
              backgroundColor: 'grey.200',
              borderRadius: 1,
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                width: `${value}%`,
                height: '100%',
                backgroundColor: value === 100 ? 'success.main' : 'primary.main',
                transition: 'width 0.3s ease',
              }}
            />
          </Box>
          <Typography variant="caption">{value}%</Typography>
        </Box>
      ),
    },
    {
      field: 'budget',
      header: 'Budget',
      render: (value) => `$${(value / 1000000).toFixed(1)}M`,
    },
    {
      field: 'risk',
      header: 'Risk',
      type: 'chip',
      chipColor: (value) => {
        const colors = { low: 'success', medium: 'warning', high: 'error' };
        return colors[value] || 'default';
      },
    },
    {
      field: 'manager',
      header: 'Manager',
    },
  ];

  // Table actions
  const actions = [
    {
      icon: <ViewIcon />,
      tooltip: 'View Details',
      onClick: (project) => console.log('View project:', project),
      color: 'primary',
    },
    {
      icon: <EditIcon />,
      tooltip: 'Edit Project',
      onClick: handleEditProject,
      color: 'primary',
    },
    {
      icon: <DeleteIcon />,
      tooltip: 'Delete Project',
      onClick: handleDeleteProject,
      color: 'error',
    },
  ];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Projects
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setModalOpen(true)}
        >
          Add Project
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Projects
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {projects.length}
                  </Typography>
                </Box>
                <BusinessIcon color="primary" sx={{ fontSize: 40 }} />
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
                    Active Projects
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {projects.filter(p => p.status === 'execution').length}
                  </Typography>
                </Box>
                <ScheduleIcon color="success" sx={{ fontSize: 40 }} />
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
                    Total Budget
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    ${(projects.reduce((sum, p) => sum + p.budget, 0) / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
                <MoneyIcon color="info" sx={{ fontSize: 40 }} />
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
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {projects.filter(p => p.risk === 'high').length}
                  </Typography>
                </Box>
                <WarningIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ML Insights Section */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <MLInsights
            type="project"
            title="AI Project Insights"
            showRefresh={true}
            onRefresh={() => {
              // Refresh insights for all projects
              projects.forEach(project => {
                dispatch(fetchProjectInsights(project.id));
              });
            }}
          />
        </Grid>
      </Grid>

      {/* Projects Table */}
      <DataTable
        data={projects}
        columns={columns}
        loading={loading}
        actions={actions}
        onRefresh={loadProjects}
        onRowClick={(project) => {
          // Load ML insights when a project is selected
          dispatch(fetchProjectInsights(project.id));
          console.log('Row clicked:', project);
        }}
        maxHeight={600}
      />

      {/* Add/Edit Project Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingProject ? 'Edit Project' : 'Add New Project'}
        maxWidth="md"
        fullWidth
      >
        <Form
          fields={formFields}
          initialValues={editingProject || {}}
          onSubmit={handleSaveProject}
          onCancel={() => setModalOpen(false)}
          submitText={editingProject ? 'Update Project' : 'Create Project'}
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

export default Projects;
