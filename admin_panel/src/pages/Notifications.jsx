import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Tabs,
  Tab,
  Stack,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
  purple: '#9C27B0',
  red: '#F44336',
  orange: '#FF9800',
  blue: '#2196F3',
};

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await api.get('/admin/alerts');
      setNotifications(response.data.alerts || []);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
      case 'severe':
        return colors.red;
      case 'moderate':
        return colors.orange;
      default:
        return colors.blue;
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
      case 'severe':
        return <WarningIcon />;
      case 'moderate':
        return <InfoIcon />;
      default:
        return <CheckCircleIcon />;
    }
  };

  const filteredNotifications = tabValue === 0
    ? notifications
    : tabValue === 1
    ? notifications.filter((n) => !n.is_resolved)
    : notifications.filter((n) => n.is_resolved);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Notifications
      </Typography>

      <Tabs
        value={tabValue}
        onChange={(e, newValue) => setTabValue(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab label="All" />
        <Tab label="Unresolved" />
        <Tab label="Resolved" />
      </Tabs>

      <Stack spacing={2}>
        {filteredNotifications.length === 0 ? (
          <Card>
            <CardContent>
              <Typography textAlign="center" color="text.secondary">
                No notifications found
              </Typography>
            </CardContent>
          </Card>
        ) : (
          filteredNotifications.map((notification) => (
            <Card
              key={notification.id}
              sx={{
                borderRadius: 2,
                borderLeft: `4px solid ${getSeverityColor(notification.severity)}`,
                '&:hover': {
                  boxShadow: 4,
                  cursor: 'pointer',
                },
              }}
              onClick={() => {
                if (notification.user_id) {
                  navigate(`/users/${notification.user_id}`);
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Box sx={{ color: getSeverityColor(notification.severity) }}>
                        {getSeverityIcon(notification.severity)}
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {notification.alert_type || 'Alert'}
                      </Typography>
                      <Chip
                        label={notification.severity || 'Info'}
                        size="small"
                        sx={{
                          bgcolor: getSeverityColor(notification.severity),
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                      {notification.is_resolved && (
                        <Chip label="Resolved" size="small" color="success" />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      User: {notification.username || 'Unknown'}
                    </Typography>
                    <Typography variant="body1">{notification.message}</Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      {new Date(notification.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))
        )}
      </Stack>
    </Box>
  );
}

export default Notifications;

