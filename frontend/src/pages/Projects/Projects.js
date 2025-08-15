import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Projects = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Projects
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Projects management page - Coming soon!
        </Typography>
      </Paper>
    </Box>
  );
};

export default Projects;
