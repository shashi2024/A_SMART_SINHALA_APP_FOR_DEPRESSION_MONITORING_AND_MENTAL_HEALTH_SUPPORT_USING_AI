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
} from '@mui/material';

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

      {/* Alerts Table */}
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
                  <TableCell>{alert.username || 'Pasindu Sandeep'}</TableCell>
                  <TableCell>{alert.alert_type || alert.email || 'pasindusandeep@gmail.com'}</TableCell>
                  <TableCell>{alert.message || '01'}</TableCell>
                  <TableCell>
                    <Chip
                      label={getRiskLabel(alert.risk_level || alert.severity) || 'Low'}
                      size="small"
                      sx={{
                        bgcolor: getRiskColor(alert.risk_level || alert.severity),
                        color: 'white',
                        fontWeight: 600,
                        borderRadius: 2,
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    {/* Actions column - empty for now */}
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
