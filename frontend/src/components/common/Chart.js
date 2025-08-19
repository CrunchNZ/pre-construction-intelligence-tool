import React, { useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tooltip,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from 'recharts';

/**
 * Reusable Chart component with various chart types and consistent styling
 * Supports line, bar, pie, and area charts with customization options
 */
const Chart = ({
  title,
  data = [],
  type = 'line',
  height = 300,
  loading = false,
  error = null,
  onRefresh,
  onDownload,
  onFullscreen,
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  colors = ['#1976d2', '#dc004e', '#2e7d32', '#ed6c02', '#9c27b0'],
  chartProps = {},
  actions = [],
  ...cardProps
}) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  // Handle menu open/close
  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);

  // Generate chart colors
  const chartColors = useMemo(() => {
    if (type === 'pie') {
      return data.map((_, index) => colors[index % colors.length]);
    }
    return colors;
  }, [type, data, colors]);

  // Render chart based on type
  const renderChart = () => {
    const commonProps = {
      data,
      ...chartProps,
    };

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            {showTooltip && <RechartsTooltip />}
            {showLegend && <Legend />}
            {Object.keys(data[0] || {}).filter(key => key !== 'name').map((key, index) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={chartColors[index % chartColors.length]}
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            {showTooltip && <RechartsTooltip />}
            {showLegend && <Legend />}
            {Object.keys(data[0] || {}).filter(key => key !== 'name').map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={chartColors[index % chartColors.length]}
              />
            ))}
          </BarChart>
        );

      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            {showTooltip && <RechartsTooltip />}
            {showLegend && <Legend />}
            {Object.keys(data[0] || {}).filter(key => key !== 'name').map((key, index) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                fill={chartColors[index % chartColors.length]}
                stroke={chartColors[index % chartColors.length]}
                fillOpacity={0.6}
              />
            ))}
          </AreaChart>
        );

      case 'pie':
        return (
          <PieChart {...commonProps}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={height * 0.3}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
              ))}
            </Pie>
            {showTooltip && <RechartsTooltip />}
            {showLegend && <Legend />}
          </PieChart>
        );

      default:
        return (
          <Box display="flex" justifyContent="center" alignItems="center" height={height}>
            <Typography color="text.secondary">
              Unsupported chart type: {type}
            </Typography>
          </Box>
        );
    }
  };

  // Render loading state
  if (loading) {
    return (
      <Card {...cardProps}>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" height={height}>
            <Typography color="text.secondary">Loading chart...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Render error state
  if (error) {
    return (
      <Card {...cardProps}>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" height={height}>
            <Typography color="error">Error loading chart: {error}</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Render chart
  return (
    <Card {...cardProps}>
      <CardContent>
        {/* Chart Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          {title && (
            <Typography variant="h6" component="h3">
              {title}
            </Typography>
          )}
          
          <Box display="flex" gap={1}>
            {/* Custom actions */}
            {actions.map((action, index) => (
              <Tooltip key={index} title={action.tooltip}>
                <IconButton size="small" onClick={action.onClick}>
                  {action.icon}
                </IconButton>
              </Tooltip>
            ))}
            
            {/* Built-in actions */}
            {onRefresh && (
              <Tooltip title="Refresh">
                <IconButton size="small" onClick={onRefresh}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            )}
            
            {onDownload && (
              <Tooltip title="Download">
                <IconButton size="small" onClick={onDownload}>
                  <DownloadIcon />
                </IconButton>
              </Tooltip>
            )}
            
            {onFullscreen && (
              <Tooltip title="Fullscreen">
                <IconButton size="small" onClick={onFullscreen}>
                  <FullscreenIcon />
                </IconButton>
              </Tooltip>
            )}
            
            {/* More options menu */}
            {(onRefresh || onDownload || onFullscreen || actions.length > 0) && (
              <>
                <IconButton size="small" onClick={handleMenuOpen}>
                  <MoreVertIcon />
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  {onRefresh && (
                    <MenuItem onClick={() => { onRefresh(); handleMenuClose(); }}>
                      <ListItemIcon><RefreshIcon fontSize="small" /></ListItemIcon>
                      <ListItemText>Refresh</ListItemText>
                    </MenuItem>
                  )}
                  {onDownload && (
                    <MenuItem onClick={() => { onDownload(); handleMenuClose(); }}>
                      <ListItemIcon><DownloadIcon fontSize="small" /></ListItemIcon>
                      <ListItemText>Download</ListItemText>
                    </MenuItem>
                  )}
                  {onFullscreen && (
                    <MenuItem onClick={() => { onFullscreen(); handleMenuClose(); }}>
                      <ListItemIcon><FullscreenIcon fontSize="small" /></ListItemIcon>
                      <ListItemText>Fullscreen</ListItemText>
                    </MenuItem>
                  )}
                </Menu>
              </>
            )}
          </Box>
        </Box>

        {/* Chart Content */}
        <ResponsiveContainer width="100%" height={height}>
          {renderChart()}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default Chart;
