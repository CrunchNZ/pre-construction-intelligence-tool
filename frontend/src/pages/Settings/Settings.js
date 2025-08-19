import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Chip,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Palette as PaletteIcon,
  Language as LanguageIcon,
  Storage as StorageIcon,
  AccountCircle as AccountCircleIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { Form, Modal, Notification } from '../../components/common';

const Settings = () => {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSetting, setEditingSetting] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [activeTab, setActiveTab] = useState(0);

  // Mock settings data - replace with actual API calls
  const mockSettings = {
    // User Preferences
    userPreferences: {
      language: 'en',
      timezone: 'UTC',
      dateFormat: 'MM/DD/YYYY',
      currency: 'USD',
      theme: 'light',
      compactMode: false,
      autoSave: true,
      notifications: {
        email: true,
        push: true,
        sms: false,
        projectUpdates: true,
        riskAlerts: true,
        financialReports: false,
        dailyDigest: true,
      },
    },
    
    // System Configuration
    systemConfig: {
      dataRefreshInterval: 5,
      maxFileSize: 10,
      backupFrequency: 'daily',
      retentionPeriod: 365,
      performanceMode: 'balanced',
      debugMode: false,
      analytics: true,
      errorReporting: true,
    },
    
    // Integration Settings
    integrations: {
      procore: {
        enabled: true,
        syncInterval: 15,
        autoSync: true,
        webhookEnabled: false,
      },
      jobpac: {
        enabled: true,
        syncInterval: 30,
        autoSync: true,
        webhookEnabled: true,
      },
      greentree: {
        enabled: false,
        syncInterval: 60,
        autoSync: false,
        webhookEnabled: false,
      },
      procurepro: {
        enabled: true,
        syncInterval: 20,
        autoSync: true,
        webhookEnabled: true,
      },
    },
    
    // Security Settings
    security: {
      twoFactorAuth: true,
      sessionTimeout: 30,
      passwordExpiry: 90,
      failedLoginAttempts: 5,
      ipWhitelist: ['192.168.1.0/24', '10.0.0.0/8'],
      auditLogging: true,
      dataEncryption: true,
    },
    
    // Notification Templates
    notificationTemplates: [
      {
        id: 1,
        name: 'Project Update',
        type: 'email',
        subject: 'Project Status Update - {projectName}',
        body: 'The project {projectName} has been updated. Current status: {status}',
        enabled: true,
      },
      {
        id: 2,
        name: 'Risk Alert',
        type: 'push',
        title: 'Risk Alert',
        body: 'High-risk item detected: {riskTitle}',
        enabled: true,
      },
      {
        id: 3,
        name: 'Financial Report',
        type: 'email',
        subject: 'Financial Report - {period}',
        body: 'Your financial report for {period} is ready for review.',
        enabled: false,
      },
    ],
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSettings(mockSettings);
    } catch (error) {
      showNotification('Failed to load settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      showNotification('Settings saved successfully', 'success');
    } catch (error) {
      showNotification('Failed to save settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value,
      },
    }));
  };

  const handleNestedSettingChange = (category, subcategory, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [subcategory]: {
          ...prev[category][subcategory],
          [key]: value,
        },
      },
    }));
  };

  const handleAddNotificationTemplate = () => {
    setEditingSetting({
      id: Date.now(),
      name: '',
      type: 'email',
      subject: '',
      body: '',
      enabled: true,
    });
    setModalOpen(true);
  };

  const handleEditNotificationTemplate = (template) => {
    setEditingSetting(template);
    setModalOpen(true);
  };

  const handleSaveNotificationTemplate = async (values) => {
    try {
      if (editingSetting.id && editingSetting.id !== Date.now()) {
        // Update existing template
        setSettings(prev => ({
          ...prev,
          notificationTemplates: prev.notificationTemplates.map(t => 
            t.id === editingSetting.id ? values : t
          ),
        }));
        showNotification('Notification template updated successfully', 'success');
      } else {
        // Add new template
        const newTemplate = { ...values, id: Date.now() };
        setSettings(prev => ({
          ...prev,
          notificationTemplates: [...prev.notificationTemplates, newTemplate],
        }));
        showNotification('Notification template created successfully', 'success');
      }
      setModalOpen(false);
    } catch (error) {
      showNotification('Failed to save notification template', 'error');
    }
  };

  const handleDeleteNotificationTemplate = (templateId) => {
    if (window.confirm('Are you sure you want to delete this notification template?')) {
      setSettings(prev => ({
        ...prev,
        notificationTemplates: prev.notificationTemplates.filter(t => t.id !== templateId),
      }));
      showNotification('Notification template deleted successfully', 'success');
    }
  };

  const getIntegrationStatus = (integration) => {
    return settings.integrations?.[integration]?.enabled ? 'Active' : 'Inactive';
  };

  const getIntegrationStatusColor = (integration) => {
    return settings.integrations?.[integration]?.enabled ? 'success' : 'error';
  };

  // Form fields for notification template
  const notificationTemplateFields = [
    {
      name: 'name',
      label: 'Template Name',
      type: 'text',
      required: 'Template name is required',
      gridProps: { xs: 12 },
    },
    {
      name: 'type',
      label: 'Type',
      type: 'select',
      required: 'Type is required',
      options: [
        { value: 'email', label: 'Email' },
        { value: 'push', label: 'Push Notification' },
        { value: 'sms', label: 'SMS' },
      ],
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'enabled',
      label: 'Enabled',
      type: 'checkbox',
      gridProps: { xs: 12, md: 6 },
    },
    {
      name: 'subject',
      label: 'Subject/Title',
      type: 'text',
      required: 'Subject is required',
      gridProps: { xs: 12 },
    },
    {
      name: 'body',
      label: 'Body/Message',
      type: 'textarea',
      required: 'Body is required',
      gridProps: { xs: 12 },
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Settings
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configure application preferences, system settings, and user preferences
          </Typography>
        </Box>
        
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadSettings}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save All Settings'}
          </Button>
        </Box>
      </Box>

      {/* Settings Categories */}
      <Grid container spacing={3}>
        {/* User Preferences */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <AccountCircleIcon color="primary" />
                <Typography variant="h6">User Preferences</Typography>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={settings.userPreferences?.language || 'en'}
                      onChange={(e) => handleSettingChange('userPreferences', 'language', e.target.value)}
                      label="Language"
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Spanish</MenuItem>
                      <MenuItem value="fr">French</MenuItem>
                      <MenuItem value="de">German</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={settings.userPreferences?.theme || 'light'}
                      onChange={(e) => handleSettingChange('userPreferences', 'theme', e.target.value)}
                      label="Theme"
                    >
                      <MenuItem value="light">Light</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="auto">Auto</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.userPreferences?.compactMode || false}
                        onChange={(e) => handleSettingChange('userPreferences', 'compactMode', e.target.checked)}
                      />
                    }
                    label="Compact Mode"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.userPreferences?.autoSave || false}
                        onChange={(e) => handleSettingChange('userPreferences', 'autoSave', e.target.checked)}
                      />
                    }
                    label="Auto-save Changes"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* System Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <StorageIcon color="primary" />
                <Typography variant="h6">System Configuration</Typography>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Data Refresh Interval (minutes)"
                    type="number"
                    value={settings.systemConfig?.dataRefreshInterval || 5}
                    onChange={(e) => handleSettingChange('systemConfig', 'dataRefreshInterval', parseInt(e.target.value))}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Max File Size (MB)"
                    type="number"
                    value={settings.systemConfig?.maxFileSize || 10}
                    onChange={(e) => handleSettingChange('systemConfig', 'maxFileSize', parseInt(e.target.value))}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.systemConfig?.debugMode || false}
                        onChange={(e) => handleSettingChange('systemConfig', 'debugMode', e.target.checked)}
                      />
                    }
                    label="Debug Mode"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.systemConfig?.analytics || false}
                        onChange={(e) => handleSettingChange('systemConfig', 'analytics', e.target.checked)}
                      />
                    }
                    label="Usage Analytics"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Integration Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <SecurityIcon color="primary" />
                <Typography variant="h6">Integration Settings</Typography>
              </Box>
              
              <Grid container spacing={2}>
                {Object.entries(settings.integrations || {}).map(([key, config]) => (
                  <Grid item xs={12} md={6} key={key}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                          <Typography variant="subtitle1" textTransform="capitalize">
                            {key}
                          </Typography>
                          <Chip
                            label={getIntegrationStatus(key)}
                            color={getIntegrationStatusColor(key)}
                            size="small"
                          />
                        </Box>
                        
                        <FormControlLabel
                          control={
                            <Switch
                              checked={config.enabled || false}
                              onChange={(e) => handleSettingChange('integrations', key, { ...config, enabled: e.target.checked })}
                            />
                          }
                          label="Enable Integration"
                        />
                        
                        <TextField
                          fullWidth
                          size="small"
                          label="Sync Interval (minutes)"
                          type="number"
                          value={config.syncInterval || 30}
                          onChange={(e) => handleSettingChange('integrations', key, { ...config, syncInterval: parseInt(e.target.value) })}
                          disabled={!config.enabled}
                          sx={{ mt: 1 }}
                        />
                        
                        <FormControlLabel
                          control={
                            <Switch
                              checked={config.autoSync || false}
                              onChange={(e) => handleSettingChange('integrations', key, { ...config, autoSync: e.target.checked })}
                              disabled={!config.enabled}
                            />
                          }
                          label="Auto-sync"
                          sx={{ mt: 1 }}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <SecurityIcon color="primary" />
                <Typography variant="h6">Security Settings</Typography>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security?.twoFactorAuth || false}
                        onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
                      />
                    }
                    label="Two-Factor Authentication"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Session Timeout (minutes)"
                    type="number"
                    value={settings.security?.sessionTimeout || 30}
                    onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Password Expiry (days)"
                    type="number"
                    value={settings.security?.passwordExpiry || 90}
                    onChange={(e) => handleSettingChange('security', 'passwordExpiry', parseInt(e.target.value))}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security?.auditLogging || false}
                        onChange={(e) => handleSettingChange('security', 'auditLogging', e.target.checked)}
                      />
                    }
                    label="Audit Logging"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <NotificationsIcon color="primary" />
                <Typography variant="h6">Notification Preferences</Typography>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.userPreferences?.notifications?.email || false}
                        onChange={(e) => handleNestedSettingChange('userPreferences', 'notifications', 'email', e.target.checked)}
                      />
                    }
                    label="Email Notifications"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.userPreferences?.notifications?.push || false}
                        onChange={(e) => handleNestedSettingChange('userPreferences', 'notifications', 'push', e.target.checked)}
                      />
                    }
                    label="Push Notifications"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.userPreferences?.notifications?.projectUpdates || false}
                        onChange={(e) => handleNestedSettingChange('userPreferences', 'notifications', 'projectUpdates', e.target.checked)}
                      />
                    }
                    label="Project Updates"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.userPreferences?.notifications?.dailyDigest || false}
                        onChange={(e) => handleNestedSettingChange('userPreferences', 'notifications', 'dailyDigest', e.target.checked)}
                      />
                    }
                    label="Daily Digest"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Templates */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Box display="flex" alignItems="center" gap={1}>
                  <NotificationsIcon color="primary" />
                  <Typography variant="h6">Notification Templates</Typography>
                </Box>
                <Button
                  size="small"
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleAddNotificationTemplate}
                >
                  Add Template
                </Button>
              </Box>
              
              <List>
                {settings.notificationTemplates?.map((template) => (
                  <ListItem key={template.id} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, mb: 1 }}>
                    <ListItemIcon>
                      <NotificationsIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={template.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {template.type === 'email' ? template.subject : template.body}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip label={template.type} size="small" variant="outlined" />
                            <Chip 
                              label={template.enabled ? 'Enabled' : 'Disabled'} 
                              size="small" 
                              color={template.enabled ? 'success' : 'default'}
                            />
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box display="flex" gap={1}>
                        <IconButton
                          size="small"
                          onClick={() => handleEditNotificationTemplate(template)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteNotificationTemplate(template.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Notification Template Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingSetting?.id && editingSetting.id !== Date.now() ? 'Edit Template' : 'Add Template'}
        maxWidth="md"
        fullWidth
      >
        <Form
          fields={notificationTemplateFields}
          initialValues={editingSetting || {}}
          onSubmit={handleSaveNotificationTemplate}
          onCancel={() => setModalOpen(false)}
          submitText={editingSetting?.id && editingSetting.id !== Date.now() ? 'Update Template' : 'Create Template'}
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

export default Settings;
