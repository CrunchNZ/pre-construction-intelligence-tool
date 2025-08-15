import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Reports = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Reports
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Report generation and export page - Coming soon!
        </Typography>
      </Paper>
    </Box>
  );
};

export default Reports;
