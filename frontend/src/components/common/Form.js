import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Chip,
  Typography,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import { LoadingButton } from '@mui/lab';

/**
 * Reusable Form component with validation and error handling
 * Supports various input types and validation schemas
 */
const Form = ({
  fields = [],
  initialValues = {},
  onSubmit,
  onCancel,
  loading = false,
  submitText = 'Submit',
  cancelText = 'Cancel',
  title,
  description,
  validationSchema,
  showCancel = true,
  maxWidth = 'md',
  spacing = 2,
}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form with default values
  useEffect(() => {
    const defaults = {};
    fields.forEach(field => {
      if (field.defaultValue !== undefined) {
        defaults[field.name] = field.defaultValue;
      }
    });
    setValues({ ...defaults, ...initialValues });
  }, [fields, initialValues]);

  // Handle input changes
  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Handle input blur (for validation)
  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    validateField(name, values[name]);
  };

  // Validate a single field
  const validateField = (name, value) => {
    if (!validationSchema || !validationSchema[name]) return '';

    const fieldSchema = validationSchema[name];
    let error = '';

    // Required validation
    if (fieldSchema.required && !value) {
      error = fieldSchema.required;
    }
    // Pattern validation
    else if (fieldSchema.pattern && !fieldSchema.pattern.test(value)) {
      error = fieldSchema.pattern.message;
    }
    // Custom validation
    else if (fieldSchema.validate) {
      error = fieldSchema.validate(value, values);
    }

    setErrors(prev => ({ ...prev, [name]: error }));
    return error;
  };

  // Validate all fields
  const validateForm = () => {
    const newErrors = {};
    let isValid = true;

    fields.forEach(field => {
      const error = validateField(field.name, values[field.name]);
      if (error) {
        newErrors[field.name] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Render form field based on type
  const renderField = (field) => {
    const {
      name,
      label,
      type = 'text',
      required = false,
      options = [],
      multiline = false,
      rows = 4,
      fullWidth = true,
      ...fieldProps
    } = field;

    const hasError = touched[name] && errors[name];
    const value = values[name] || '';

    switch (type) {
      case 'select':
        return (
          <FormControl fullWidth={fullWidth} error={!!hasError} required={required}>
            <InputLabel>{label}</InputLabel>
            <Select
              value={value}
              label={label}
              onChange={(e) => handleChange(name, e.target.value)}
              onBlur={() => handleBlur(name)}
              {...fieldProps}
            >
              {options.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {hasError && <FormHelperText>{hasError}</FormHelperText>}
          </FormControl>
        );

      case 'multiselect':
        return (
          <FormControl fullWidth={fullWidth} error={!!hasError} required={required}>
            <InputLabel>{label}</InputLabel>
            <Select
              multiple
              value={Array.isArray(value) ? value : []}
              label={label}
              onChange={(e) => handleChange(name, e.target.value)}
              onBlur={() => handleBlur(name)}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
              {...fieldProps}
            >
              {options.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {hasError && <FormHelperText>{hasError}</FormHelperText>}
          </FormControl>
        );

      case 'textarea':
        return (
          <TextField
            fullWidth={fullWidth}
            label={label}
            value={value}
            onChange={(e) => handleChange(name, e.target.value)}
            onBlur={() => handleBlur(name)}
            multiline
            rows={rows}
            required={required}
            error={!!hasError}
            helperText={hasError}
            {...fieldProps}
          />
        );

      default:
        return (
          <TextField
            fullWidth={fullWidth}
            label={label}
            type={type}
            value={value}
            onChange={(e) => handleChange(name, e.target.value)}
            onBlur={() => handleBlur(name)}
            required={required}
            error={!!hasError}
            helperText={hasError}
            {...fieldProps}
          />
        );
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        maxWidth,
        mx: 'auto',
        p: 3,
      }}
    >
      {/* Form Header */}
      {title && (
        <Box mb={3}>
          <Typography variant="h5" component="h2" gutterBottom>
            {title}
          </Typography>
          {description && (
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          )}
        </Box>
      )}

      {/* Form Fields */}
      <Grid container spacing={spacing}>
        {fields.map((field) => (
          <Grid item key={field.name} xs={12} {...field.gridProps}>
            {renderField(field)}
          </Grid>
        ))}
      </Grid>

      {/* Form Actions */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          justifyContent: 'flex-end',
          mt: 4,
          pt: 2,
          borderTop: '1px solid',
          borderColor: 'divider',
        }}
      >
        {showCancel && (
          <Button
            variant="outlined"
            onClick={onCancel}
            disabled={loading || isSubmitting}
          >
            {cancelText}
          </Button>
        )}
        
        <LoadingButton
          type="submit"
          variant="contained"
          loading={loading || isSubmitting}
          disabled={loading || isSubmitting}
        >
          {submitText}
        </LoadingButton>
      </Box>
    </Box>
  );
};

export default Form;
