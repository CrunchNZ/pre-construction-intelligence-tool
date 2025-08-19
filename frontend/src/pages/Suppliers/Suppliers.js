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
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Business as BusinessIcon,
  Star as StarIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { DataTable, Modal, Form, Notification } from '../../components/common';

const Suppliers = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  // Mock data - replace with actual API calls
  const mockSuppliers = [
    {
      id: 1,
      name: 'ABC Construction Supplies',
      contact: 'John Smith',
      email: 'john@abc.com',
      phone: '+1-555-0123',
      category: 'Materials',
      rating: 4.8,
      status: 'active',
      projects: 15,
      totalValue: 2500000,
      onTimeDelivery: 95,
      qualityScore: 92,
      lastProject: '2024-01-10',
    },
    {
      id: 2,
      name: 'XYZ Equipment Rentals',
      contact: 'Sarah Johnson',
      email: 'sarah@xyz.com',
      phone: '+1-555-0456',
      category: 'Equipment',
      rating: 4.2,
      status: 'active',
      projects: 8,
      totalValue: 1800000,
      onTimeDelivery: 88,
      qualityScore: 85,
      lastProject: '2024-01-08',
    },
    {
      id: 3,
      name: 'Premium Steel Co.',
      contact: 'Mike Davis',
      email: 'mike@premiumsteel.com',
      phone: '+1-555-0789',
      category: 'Materials',
      rating: 4.9,
      status: 'active',
      projects: 22,
      totalValue: 4200000,
      onTimeDelivery: 98,
      qualityScore: 96,
      lastProject: '2024-01-12',
    },
    {
      id: 4,
      name: 'Safety First Equipment',
      contact: 'Lisa Chen',
      email: 'lisa@safetyfirst.com',
      phone: '+1-555-0321',
      category: 'Safety',
      rating: 4.5,
      status: 'inactive',
      projects: 12,
      totalValue: 1500000,
      onTimeDelivery: 90,
      qualityScore: 88,
      lastProject: '2023-12-15',
    },
  ];

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSuppliers(mockSuppliers);
    } catch (error) {
      showNotification('Failed to load suppliers', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleAddSupplier = () => {
    setEditingSupplier(null);
    setModalOpen(true);
  };

  const handleEditSupplier = (supplier) => {
    setEditingSupplier(supplier);
    setModalOpen(true);
  };

  const handleDeleteSupplier = async (supplier) => {
    if (window.confirm(`Are you sure you want to delete "${supplier.name}"?`)) {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        setSuppliers(prev => prev.filter(s => s.id !== supplier.id));
        showNotification('Supplier deleted successfully', 'success');
      } catch (error) {
        showNotification('Failed to delete supplier', 'error');
      }
    }
  };

  const handleSaveSupplier = async (values) => {
    try {
      if (editingSupplier) {
        // Update existing supplier
        const updatedSupplier = { ...editingSupplier, ...values };
        setSuppliers(prev => prev.map(s => s.id === editingSupplier.id ? updatedSupplier : s));
        showNotification('Supplier updated successfully', 'success');
      } else {
        // Add new supplier
        const newSupplier = {
          id: Date.now(),
          ...values,
          rating: 0,
          projects: 0,
          totalValue: 0,
          onTimeDelivery: 0,
          qualityScore: 0,
          lastProject: null,
        };
        setSuppliers(prev => [...prev, newSupplier]);
        showNotification('Supplier created successfully', 'success');
      }
      setModalOpen(false);
    } catch (error) {
      showNotification('Failed to save supplier', 'error');
    }
  };

  // Form fields configuration
  const formFields = [
    {
      name: 'name',
      label: 'Supplier Name',
      type: 'text',
      required: 'Supplier name is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'contact',
      label: 'Contact Person',
      type: 'text',
      required: 'Contact person is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'email',
      label: 'Email',
      type: 'email',
      required: 'Valid email is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'phone',
      label: 'Phone',
      type: 'tel',
      required: 'Phone number is required',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'category',
      label: 'Category',
      type: 'select',
      required: 'Category is required',
      options: [
        { value: 'Materials', label: 'Materials' },
        { value: 'Equipment', label: 'Equipment' },
        { value: 'Labor', label: 'Labor' },
        { value: 'Safety', label: 'Safety' },
        { value: 'Technology', label: 'Technology' },
        { value: 'Other', label: 'Other' },
      ],
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      required: 'Status is required',
      options: [
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' },
        { value: 'pending', label: 'Pending Review' },
        { value: 'suspended', label: 'Suspended' },
      ],
      gridProps: { xs: 12, md: 6 },
    },
  ];

  // Table columns configuration
  const columns = [
    {
      field: 'name',
      header: 'Supplier Name',
      render: (value, row) => (
        <Box>
          <Typography variant="subtitle2" fontWeight="medium">
            {value}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {row.category}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'contact',
      header: 'Contact',
      render: (value, row) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {value}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {row.email}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'rating',
      header: 'Rating',
      render: (value) => (
        <Box display="flex" alignItems="center" gap={0.5}>
          <StarIcon sx={{ color: 'warning.main', fontSize: 16 }} />
          <Typography variant="body2" fontWeight="medium">
            {value.toFixed(1)}
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
      field: 'projects',
      header: 'Projects',
      render: (value) => (
        <Typography variant="body2" fontWeight="medium">
          {value}
        </Typography>
      ),
    },
    {
      field: 'totalValue',
      header: 'Total Value',
      render: (value) => `$${(value / 1000000).toFixed(1)}M`,
    },
    {
      field: 'onTimeDelivery',
      header: 'On-Time Delivery',
      render: (value) => (
        <Box display="flex" alignItems="center" gap={1}>
          <Box
            sx={{
              width: 40,
              height: 6,
              backgroundColor: 'grey.200',
              borderRadius: 1,
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                width: `${value}%`,
                height: '100%',
                backgroundColor: value >= 90 ? 'success.main' : value >= 80 ? 'warning.main' : 'error.main',
              }}
            />
          </Box>
          <Typography variant="caption">{value}%</Typography>
        </Box>
      ),
    },
    {
      field: 'qualityScore',
      header: 'Quality Score',
      render: (value) => (
        <Box display="flex" alignItems="center" gap={1}>
          <Box
            sx={{
              width: 40,
              height: 6,
              backgroundColor: 'grey.200',
              borderRadius: 1,
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                width: `${value}%`,
                height: '100%',
                backgroundColor: value >= 90 ? 'success.main' : value >= 80 ? 'warning.main' : 'error.main',
              }}
            />
          </Box>
          <Typography variant="caption">{value}%</Typography>
        </Box>
      ),
    },
  ];

  // Table actions
  const actions = [
    {
      icon: <ViewIcon />,
      tooltip: 'View Details',
      onClick: (supplier) => console.log('View supplier:', supplier),
      color: 'primary',
    },
    {
      icon: <EditIcon />,
      tooltip: 'Edit Supplier',
      onClick: handleEditSupplier,
      color: 'primary',
    },
    {
      icon: <DeleteIcon />,
      tooltip: 'Delete Supplier',
      onClick: handleDeleteSupplier,
      color: 'error',
    },
  ];

  const getStatusColor = (status) => {
    const colors = {
      active: 'success',
      inactive: 'error',
      pending: 'warning',
      suspended: 'error',
    };
    return colors[status] || 'default';
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Suppliers
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage supplier relationships, track performance, and monitor quality metrics
          </Typography>
        </Box>
        
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddSupplier}
        >
          Add Supplier
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
                    Total Suppliers
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {suppliers.length}
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
                    Active Suppliers
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="success.main">
                    {suppliers.filter(s => s.status === 'active').length}
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
                    Avg Rating
                  </Typography>
                  <Typography variant="h4" component="div" fontWeight="bold" color="warning.main">
                    {(suppliers.reduce((sum, s) => sum + s.rating, 0) / suppliers.length).toFixed(1)}
                  </Typography>
                </Box>
                <StarIcon color="warning" sx={{ fontSize: 40 }} />
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
                    {suppliers.filter(s => s.onTimeDelivery < 80 || s.qualityScore < 80).length}
                  </Typography>
                </Box>
                <WarningIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Performance Insight:</strong> 3 suppliers have delivery rates below 90%. 
          Consider reviewing contracts and implementing improvement plans for these suppliers.
        </Typography>
      </Alert>

      {/* Suppliers Table */}
      <DataTable
        data={suppliers}
        columns={columns}
        loading={loading}
        actions={actions}
        onRefresh={loadSuppliers}
        onRowClick={(supplier) => console.log('Row clicked:', supplier)}
        maxHeight={600}
      />

      {/* Add/Edit Supplier Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingSupplier ? 'Edit Supplier' : 'Add New Supplier'}
        maxWidth="md"
        fullWidth
      >
        <Form
          fields={formFields}
          initialValues={editingSupplier || {}}
          onSubmit={handleSaveSupplier}
          onCancel={() => setModalOpen(false)}
          submitText={editingSupplier ? 'Update Supplier' : 'Create Supplier'}
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

export default Suppliers;
