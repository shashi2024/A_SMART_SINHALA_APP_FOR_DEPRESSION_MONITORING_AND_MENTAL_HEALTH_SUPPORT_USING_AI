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
  LocalHospital as LocalHospitalIcon,
  PersonAdd as PersonAddIcon,
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
      const response = await api.get('/admin/notifications');
      setNotifications(response.data.notifications || []);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await api.post(`/admin/notifications/${notificationId}/read`);
      // Reload notifications
      loadNotifications();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
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
    ? notifications.filter((n) => !n.is_read)
    : notifications.filter((n) => n.is_read);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'doctor_assignment':
        return <LocalHospitalIcon />;
      default:
        return <NotificationsIcon />;
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
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Notifications
      </Typography>

      <Tabs
        value={tabValue}
        onChange={(e, newValue) => setTabValue(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab label="All" />
        <Tab label="Unread" />
        <Tab label="Read" />
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
                borderLeft: `4px solid ${notification.type === 'doctor_assignment' ? colors.darkGreen : colors.blue}`,
                bgcolor: notification.is_read ? 'transparent' : colors.veryLightBlue,
                '&:hover': {
                  boxShadow: 4,
                  cursor: 'pointer',
                },
              }}
              onClick={() => {
                if (!notification.is_read) {
                  handleMarkAsRead(notification.id);
                }
                if (notification.patient_id) {
                  // Navigate to patient details if available
                  navigate(`/patients-risk`);
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Box sx={{ color: notification.type === 'doctor_assignment' ? colors.darkGreen : colors.blue }}>
                        {getNotificationIcon(notification.type)}
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {notification.title || 'Notification'}
                      </Typography>
                      {notification.type === 'doctor_assignment' && (
                        <Chip
                          label="Assignment"
                          size="small"
                          sx={{
                            bgcolor: colors.darkGreen,
                            color: 'white',
                            fontWeight: 600,
                          }}
                        />
                      )}
                      {!notification.is_read && (
                        <Chip label="New" size="small" color="primary" />
                      )}
                    </Box>
                    {notification.patient_username && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Patient: {notification.patient_username}
                      </Typography>
                    )}
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

