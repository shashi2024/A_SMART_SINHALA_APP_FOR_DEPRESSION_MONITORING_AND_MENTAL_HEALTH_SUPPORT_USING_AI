import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip,
  CircularProgress,
} from '@mui/material';

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState(null); // null, true, or false

  useEffect(() => {
    loadAlerts();
  }, [filter]);

  const loadAlerts = async () => {
    try {
      const params = filter !== null ? { resolved: filter } : {};
      const response = await api.get('/admin/alerts', { params });
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      await api.post(`/admin/alerts/${alertId}/resolve`);
      loadAlerts();
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <Typography variant="h4" gutterBottom>
        Alerts Management
      </Typography>

      <div style={{ marginBottom: 20 }}>
        <Button
          variant={filter === null ? 'contained' : 'outlined'}
          onClick={() => setFilter(null)}
          style={{ marginRight: 10 }}
        >
          All
        </Button>
        <Button
          variant={filter === false ? 'contained' : 'outlined'}
          onClick={() => setFilter(false)}
          style={{ marginRight: 10 }}
        >
          Unresolved
        </Button>
        <Button
          variant={filter === true ? 'contained' : 'outlined'}
          onClick={() => setFilter(true)}
        >
          Resolved
        </Button>
      </div>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Message</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {alerts.map((alert) => (
              <TableRow key={alert.id}>
                <TableCell>{alert.username}</TableCell>
                <TableCell>{alert.alert_type}</TableCell>
                <TableCell>
                  <Chip
                    label={alert.severity}
                    color={getSeverityColor(alert.severity)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{alert.message}</TableCell>
                <TableCell>
                  {new Date(alert.created_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {alert.is_resolved ? (
                    <Chip label="Resolved" color="success" size="small" />
                  ) : (
                    <Chip label="Active" color="warning" size="small" />
                  )}
                </TableCell>
                <TableCell>
                  {!alert.is_resolved && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => resolveAlert(alert.id)}
                    >
                      Resolve
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

export default Alerts;

