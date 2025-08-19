import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  TextField,
  Box,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Typography,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

/**
 * Reusable DataTable component with sorting, filtering, and pagination
 * Supports custom cell renderers and action buttons
 */
const DataTable = ({
  data = [],
  columns = [],
  loading = false,
  searchable = true,
  filterable = true,
  pageable = true,
  onRefresh,
  onRowClick,
  actions = [],
  maxHeight = 400,
}) => {
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');

  // Handle sorting
  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  // Handle page change
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Filter and sort data
  const processedData = useMemo(() => {
    let filteredData = data;

    // Apply search filter
    if (searchTerm && searchable) {
      filteredData = data.filter((row) =>
        Object.values(row).some((value) =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Apply sorting
    if (orderBy) {
      filteredData.sort((a, b) => {
        const aValue = a[orderBy];
        const bValue = b[orderBy];
        
        if (aValue < bValue) return order === 'asc' ? -1 : 1;
        if (aValue > bValue) return order === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filteredData;
  }, [data, searchTerm, orderBy, order, searchable]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pageable) return processedData;
    const startIndex = page * rowsPerPage;
    return processedData.slice(startIndex, startIndex + rowsPerPage);
  }, [processedData, page, rowsPerPage, pageable]);

  // Render cell content
  const renderCell = (row, column) => {
    const value = row[column.field];
    
    if (column.render) {
      return column.render(value, row);
    }

    if (column.type === 'chip') {
      return (
        <Chip
          label={value}
          color={column.chipColor || 'default'}
          size="small"
          variant="outlined"
        />
      );
    }

    if (column.type === 'status') {
      const statusColors = {
        active: 'success',
        inactive: 'error',
        pending: 'warning',
        completed: 'info',
      };
      return (
        <Chip
          label={value}
          color={statusColors[value] || 'default'}
          size="small"
        />
      );
    }

    return value;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={4}>
        <CircularProgress />
        <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
          Loading data...
        </Typography>
      </Box>
    );
  }

  return (
    <Paper elevation={1}>
      {/* Search and Filter Bar */}
      {(searchable || filterable) && (
        <Box p={2} borderBottom="1px solid #e0e0e0">
          <Box display="flex" gap={2} alignItems="center">
            {searchable && (
              <TextField
                size="small"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon color="action" />,
                }}
                sx={{ minWidth: 200 }}
              />
            )}
            
            {filterable && (
              <Tooltip title="Advanced filters">
                <IconButton size="small">
                  <FilterIcon />
                </IconButton>
              </Tooltip>
            )}
            
            {onRefresh && (
              <Tooltip title="Refresh data">
                <IconButton size="small" onClick={onRefresh}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            )}
            
            <Box flexGrow={1} />
            
            <Typography variant="body2" color="text.secondary">
              {processedData.length} of {data.length} records
            </Typography>
          </Box>
        </Box>
      )}

      {/* Table */}
      <TableContainer sx={{ maxHeight }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.field}
                  sortDirection={orderBy === column.field ? order : false}
                  sx={{
                    fontWeight: 'bold',
                    backgroundColor: 'background.paper',
                  }}
                >
                  {column.sortable !== false ? (
                    <TableSortLabel
                      active={orderBy === column.field}
                      direction={orderBy === column.field ? order : 'asc'}
                      onClick={() => handleRequestSort(column.field)}
                    >
                      {column.header}
                    </TableSortLabel>
                  ) : (
                    column.header
                  )}
                </TableCell>
              ))}
              
              {actions.length > 0 && (
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: 'background.paper' }}>
                  Actions
                </TableCell>
              )}
            </TableRow>
          </TableHead>
          
          <TableBody>
            {paginatedData.map((row, index) => (
              <TableRow
                key={row.id || index}
                hover
                onClick={() => onRowClick && onRowClick(row)}
                sx={{
                  cursor: onRowClick ? 'pointer' : 'default',
                  '&:hover': onRowClick ? { backgroundColor: 'action.hover' } : {},
                }}
              >
                {columns.map((column) => (
                  <TableCell key={column.field}>
                    {renderCell(row, column)}
                  </TableCell>
                ))}
                
                {actions.length > 0 && (
                  <TableCell>
                    <Box display="flex" gap={1}>
                      {actions.map((action, actionIndex) => (
                        <Tooltip key={actionIndex} title={action.tooltip}>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              action.onClick(row);
                            }}
                            color={action.color || 'default'}
                          >
                            {action.icon}
                          </IconButton>
                        </Tooltip>
                      ))}
                    </Box>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {pageable && (
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={processedData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      )}
    </Paper>
  );
};

export default DataTable;
