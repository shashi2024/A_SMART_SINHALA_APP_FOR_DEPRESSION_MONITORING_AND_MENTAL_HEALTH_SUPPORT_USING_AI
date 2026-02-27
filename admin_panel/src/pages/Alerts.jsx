import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Tabs,
  Tab,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
  lightPink: '#FFF5F5',
};

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState(0); // 0: All, 1: Unresolved, 2: Resolved

  useEffect(() => {
    loadAlerts();
  }, [filter]);

  const loadAlerts = async () => {
    try {
      let params = {};
      if (filter === 1) {
        params.resolved = false;
      } else if (filter === 2) {
        params.resolved = true;
      }
      const response = await api.get('/admin/alerts', { params });
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'severe':
      case 'high':
        return colors.red || '#F44336';
      case 'moderate':
        return colors.orange || '#FF9800';
      default:
        return colors.darkGreen;
    }
  };

  const getRiskLabel = (riskLevel) => {
    switch (riskLevel) {
      case 'severe':
      case 'high':
        return 'High';
      case 'moderate':
        return 'Mid';
      default:
        return 'Low';
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      await api.post(`/admin/alerts/${alertId}/resolve`);
      // Reload alerts after resolving
      loadAlerts();
    } catch (error) {
      console.error('Failed to resolve alert:', error);
      alert('Failed to resolve alert. Please try again.');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return dateString;
    }
  };

  const getStatusChip = (isResolved, riskLevel) => {
    if (isResolved) {
      return (
        <Chip
          label="RESOLVED"
          size="small"
          icon={<CheckCircleIcon />}
          sx={{
            bgcolor: colors.darkGreen,
            color: 'white',
            fontWeight: 600,
            borderRadius: 2,
          }}
        />
      );
    } else {
      return (
        <Chip
          label={getRiskLabel(riskLevel || 'low')}
          size="small"
          icon={<WarningIcon />}
          sx={{
            bgcolor: getRiskColor(riskLevel || 'low'),
            color: 'white',
            fontWeight: 600,
            borderRadius: 2,
          }}
        />
      );
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 4 }}>
        Alerts Management
      </Typography>

      {/* Filter Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={filter}
          onChange={(e, newValue) => setFilter(newValue)}
          sx={{
            '& .MuiTab-root': {
              textTransform: 'none',
              fontSize: '16px',
              fontWeight: filter === 0 ? 600 : 400,
              color: filter === 0 ? colors.darkGreen : '#999',
              '&.Mui-selected': {
                color: colors.darkGreen,
                fontWeight: 600,
              },
            },
            '& .MuiTabs-indicator': {
              bgcolor: colors.darkGreen,
            },
          }}
        >
          <Tab label="All" />
          <Tab label="UNRESOLVED" />
          <Tab label="RESOLVED" />
        </Tabs>
      </Box>

      {/* Alerts Table1 */}
      <TableContainer
        component={Paper}
        sx={{
          borderRadius: 3,
          boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
        }}
      >
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F5F5F5' }}>
              <TableCell sx={{ fontWeight: 'bold' }}>User</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Message</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {alerts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    No alerts found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              alerts.map((alert, index) => (
                <TableRow
                  key={alert.id || index}
                  sx={{
                    bgcolor: index % 2 === 0 ? colors.lightPink : 'white',
                  }}
                >
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {alert.username || 'Unknown User'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={alert.alert_type || 'Unknown'}
                      size="small"
                      sx={{
                        bgcolor: alert.alert_type === 'crisis' ? '#F44336' : '#FF9800',
                        color: 'white',
                        fontWeight: 500,
                        textTransform: 'capitalize',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ maxWidth: 300 }}>
                      {alert.message || 'No message available'}
                    </Typography>
                    {alert.created_at && (
                      <Typography variant="caption" sx={{ color: '#666', display: 'block', mt: 0.5 }}>
                        {formatDate(alert.created_at)}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {getStatusChip(alert.is_resolved, alert.risk_level || alert.severity)}
                  </TableCell>
                  <TableCell>
                    {!alert.is_resolved && (
                      <Tooltip title="Mark as resolved">
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleResolveAlert(alert.id)}
                          sx={{
                            color: colors.darkGreen,
                            borderColor: colors.darkGreen,
                            '&:hover': {
                              borderColor: colors.darkGreen,
                              bgcolor: colors.paleSageGreen,
                            },
                          }}
                        >
                          Resolve
                        </Button>
                      </Tooltip>
                    )}
                    {alert.is_resolved && (
                      <Typography variant="caption" sx={{ color: '#666' }}>
                        Resolved
                      </Typography>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default Alerts;
