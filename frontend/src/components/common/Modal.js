import React, { useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  Box,
  Fade,
  Slide,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

/**
 * Reusable Modal component with consistent styling and accessibility
 * Supports various sizes, animations, and content types
 */
const Modal = ({
  open = false,
  onClose,
  title,
  children,
  actions,
  maxWidth = 'sm',
  fullWidth = false,
  fullScreen = false,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
  closeOnBackdropClick = true,
  showCloseButton = true,
  transition = 'fade', // 'fade' or 'slide'
  slideDirection = 'up',
  contentPadding = 2,
  titleVariant = 'h6',
  elevation = 24,
  ...dialogProps
}) => {
  // Handle escape key and backdrop click
  const handleClose = (event, reason) => {
    if (reason === 'backdropClick' && !closeOnBackdropClick) {
      return;
    }
    if (onClose) {
      onClose(event, reason);
    }
  };

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [open]);

  // Transition components
  const TransitionComponent = transition === 'slide' ? Slide : Fade;
  const transitionProps = transition === 'slide' 
    ? { direction: slideDirection }
    : {};

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      fullScreen={fullScreen}
      disableBackdropClick={disableBackdropClick}
      disableEscapeKeyDown={disableEscapeKeyDown}
      TransitionComponent={TransitionComponent}
      transitionDuration={300}
      {...transitionProps}
      PaperProps={{
        elevation,
        sx: {
          borderRadius: fullScreen ? 0 : 2,
          minWidth: fullScreen ? '100vw' : 320,
          maxHeight: fullScreen ? '100vh' : '90vh',
        },
      }}
      {...dialogProps}
    >
      {/* Modal Header */}
      {title && (
        <DialogTitle
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            pb: 1,
            pr: showCloseButton ? 1 : 2,
          }}
        >
          <Typography variant={titleVariant} component="h2">
            {title}
          </Typography>
          
          {showCloseButton && (
            <IconButton
              aria-label="close"
              onClick={handleClose}
              sx={{
                color: 'text.secondary',
                '&:hover': {
                  color: 'text.primary',
                },
              }}
            >
              <CloseIcon />
            </IconButton>
          )}
        </DialogTitle>
      )}

      {/* Modal Content */}
      <DialogContent
        sx={{
          p: contentPadding,
          ...(fullScreen && {
            p: 3,
          }),
        }}
      >
        {children}
      </DialogContent>

      {/* Modal Actions */}
      {actions && (
        <DialogActions
          sx={{
            p: 2,
            pt: 1,
            gap: 1,
            justifyContent: 'flex-end',
          }}
        >
          {actions}
        </DialogActions>
      )}
    </Dialog>
  );
};

export default Modal;
