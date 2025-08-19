import React, { useState, useEffect } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Box,
  Typography,
  IconButton,
  Collapse,
  Paper,
} from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

/**
 * Reusable Notification component for displaying various message types
 * Supports auto-dismiss, manual close, and different severity levels
 */
const Notification = ({
  open = false,
  message = '',
  title = '',
  severity = 'info',
  variant = 'filled', // 'filled', 'outlined', 'standard'
  autoHideDuration = 6000,
  onClose,
  onExited,
  position = 'bottom-right', // 'top-left', 'top-center', 'top-right', 'bottom-left', 'bottom-center', 'bottom-right'
  showIcon = true,
  showCloseButton = true,
  persistent = false,
  maxWidth = 400,
  elevation = 6,
  ...alertProps
}) => {
  const [isOpen, setIsOpen] = useState(open);
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Update open state when prop changes
  useEffect(() => {
    setIsOpen(open);
  }, [open]);

  // Auto-hide functionality
  useEffect(() => {
    if (isOpen && !persistent && autoHideDuration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, autoHideDuration);

      return () => clearTimeout(timer);
    }
  }, [isOpen, persistent, autoHideDuration]);

  // Handle close
  const handleClose = (event, reason) => {
    if (reason === 'clickaway' && persistent) {
      return;
    }
    
    setIsOpen(false);
    if (onClose) {
      onClose(event, reason);
    }
  };

  // Handle collapse toggle
  const handleCollapseToggle = () => {
    setIsCollapsed(!isCollapsed);
  };

  // Get severity icon
  const getSeverityIcon = () => {
    if (!showIcon) return null;

    const icons = {
      success: <SuccessIcon />,
      error: <ErrorIcon />,
      warning: <WarningIcon />,
      info: <InfoIcon />,
    };

    return icons[severity] || icons.info;
  };

  // Get position styles
  const getPositionStyles = () => {
    const positions = {
      'top-left': { top: 16, left: 16 },
      'top-center': { top: 16, left: '50%', transform: 'translateX(-50%)' },
      'top-right': { top: 16, right: 16 },
      'bottom-left': { bottom: 16, left: 16 },
      'bottom-center': { bottom: 16, left: '50%', transform: 'translateX(-50%)' },
      'bottom-right': { bottom: 16, right: 16 },
    };

    return positions[position] || positions['bottom-right'];
  };

  // Render notification content
  const renderContent = () => {
    if (variant === 'standard') {
      return (
        <Paper elevation={elevation} sx={{ maxWidth, width: '100%' }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              p: 2,
              gap: 1,
            }}
          >
            {getSeverityIcon()}
            
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              {title && (
                <Typography variant="subtitle2" fontWeight="medium" gutterBottom>
                  {title}
                </Typography>
              )}
              
              <Collapse in={!isCollapsed}>
                <Typography variant="body2" color="text.secondary">
                  {message}
                </Typography>
              </Collapse>
            </Box>

            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {message.length > 100 && (
                <IconButton
                  size="small"
                  onClick={handleCollapseToggle}
                  sx={{ p: 0.5 }}
                >
                  <Typography variant="caption">
                    {isCollapsed ? 'Show more' : 'Show less'}
                  </Typography>
                </IconButton>
              )}
              
              {showCloseButton && (
                <IconButton
                  size="small"
                  onClick={handleClose}
                  sx={{ p: 0.5 }}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              )}
            </Box>
          </Box>
        </Paper>
      );
    }

    // Use Alert component for filled/outlined variants
    return (
      <Alert
        severity={severity}
        variant={variant}
        icon={getSeverityIcon()}
        onClose={showCloseButton ? handleClose : undefined}
        sx={{ maxWidth, width: '100%' }}
        {...alertProps}
      >
        {title && <AlertTitle>{title}</AlertTitle>}
        <Collapse in={!isCollapsed}>
          {message}
        </Collapse>
        
        {message.length > 100 && (
          <Box mt={1}>
            <Typography
              variant="caption"
              color="inherit"
              sx={{ cursor: 'pointer', textDecoration: 'underline' }}
              onClick={handleCollapseToggle}
            >
              {isCollapsed ? 'Show more' : 'Show less'}
            </Typography>
          </Box>
        )}
      </Alert>
    );
  };

  return (
    <Snackbar
      open={isOpen}
      autoHideDuration={persistent ? null : autoHideDuration}
      onClose={handleClose}
      onExited={onExited}
      anchorOrigin={{
        vertical: position.includes('top') ? 'top' : 'bottom',
        horizontal: position.includes('left') ? 'left' : position.includes('right') ? 'right' : 'center',
      }}
      sx={{
        position: 'fixed',
        zIndex: 1400,
        ...getPositionStyles(),
      }}
    >
      {renderContent()}
    </Snackbar>
  );
};

export default Notification;
