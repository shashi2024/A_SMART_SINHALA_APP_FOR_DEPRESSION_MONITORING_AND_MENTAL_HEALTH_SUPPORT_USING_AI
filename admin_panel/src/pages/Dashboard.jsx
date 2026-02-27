import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Avatar,
  Button,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  Chip,
} from '@mui/material';
import {
  CalendarToday,
  People,
  Assignment,
  Videocam,
  TrendingUp,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { useAuth } from '../contexts/AuthContext';

const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
  lightPink: '#FFF5F5',
};

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      if (error.response?.status === 403) {
        alert('Access denied: Admin privileges required');
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return '#4CAF50';
      case 'declined':
        return '#F44336';
      case 'pending':
        return '#2196F3';
      case 'ongoing':
        return '#FF9800';
      default:
        return '#9E9E9E';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>No data available</Typography>
      </Box>
    );
  }

  const stats = dashboardData.statistics || {};
  const demographics = dashboardData.demographics || {};
  const appointmentRequests = dashboardData.appointment_requests || [];
  const todayAppointments = dashboardData.today_appointments || [];

  // Prepare data for donut chart
  const chartData = [
    { name: 'Male', value: demographics.male?.count || 0, color: '#FF9800' },
    { name: 'Female', value: demographics.female?.count || 0, color: '#9C27B0' },
    { name: 'Other', value: demographics.other?.count || 0, color: '#2196F3' },
  ];

  const metricCards = [
    {
      title: 'Appointments',
      value: formatNumber(stats.appointments || 0),
      icon: <CalendarToday sx={{ fontSize: 40 }} />,
      color: '#9C27B0',
      bgColor: '#F3E5F5',
    },
    {
      title: 'Total Patients',
      value: formatNumber(stats.total_patients || 0),
      icon: <People sx={{ fontSize: 40 }} />,
      color: '#F44336',
      bgColor: '#FFEBEE',
    },
    {
      title: 'Clinic Consulting',
      value: formatNumber(stats.clinic_consulting || 0),
      icon: <Assignment sx={{ fontSize: 40 }} />,
      color: '#FF9800',
      bgColor: '#FFF3E0',
    },
    {
      title: 'Video Consulting',
      value: formatNumber(stats.video_consulting || 0),
      icon: <Videocam sx={{ fontSize: 40 }} />,
      color: '#2196F3',
      bgColor: '#E3F2FD',
    },
  ];

  return (
    <Box sx={{ bgcolor: colors.lightPink, minHeight: '100vh', p: 4 }}>
      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {metricCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                borderRadius: 3,
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                },
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography
                      variant="h4"
                      sx={{
                        fontWeight: 'bold',
                        color: '#333',
                        mb: 1,
                      }}
                    >
                      {card.value}
      </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#666',
                        fontSize: '14px',
                      }}
                    >
                      {card.title}
          </Typography>
                  </Box>
                  <Box
                    sx={{
                      bgcolor: card.bgColor,
                      borderRadius: '50%',
                      p: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Box sx={{ color: card.color }}>{card.icon}</Box>
                  </Box>
                </Box>
        </CardContent>
      </Card>
          </Grid>
        ))}
      </Grid>

      {/* Three Column Layout */}
      <Grid container spacing={3}>
        {/* Left Column - Appointment Request */}
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              height: '100%',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#333' }}>
                  Appointment Request
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: '#2196F3',
                    cursor: 'pointer',
                    '&:hover': { textDecoration: 'underline' },
                  }}
                  onClick={() => navigate('/alerts')}
                >
                  View All
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {appointmentRequests.length > 0 ? (
                  appointmentRequests.map((request, index) => (
                    <Box
                      key={request.id || index}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: '#F5F5F5',
                        '&:hover': { bgcolor: '#EEEEEE' },
                      }}
                    >
                      <Avatar
                        sx={{
                          bgcolor: colors.darkGreen,
                          width: 40,
                          height: 40,
                        }}
                      >
                        {request.username?.charAt(0)?.toUpperCase() || 'U'}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#333' }}>
                          {request.username || 'Unknown User'}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#666', fontSize: '12px' }}>
                          {request.details || 'Pending request'}
                        </Typography>
                      </Box>
                  <Chip
                        label={request.status || 'Pending'}
                    size="small"
                        sx={{
                          bgcolor: getStatusColor(request.status),
                          color: 'white',
                          fontWeight: 500,
                          fontSize: '11px',
                        }}
                      />
                    </Box>
                  ))
                ) : (
                  <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 3 }}>
                    No appointment requests
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Middle Column - Patients Overview */}
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              height: '100%',
            }}
          >
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#333', mb: 3 }}>
                patients
              </Typography>

              {/* New/Old Patients Stats */}
              <Box sx={{ mb: 3 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    mb: 2,
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: '#E3F2FD',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <People sx={{ color: '#2196F3', fontSize: 24 }} />
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: '#333' }}>
                        {formatNumber(stats.new_patients || 0)}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#666', fontSize: '12px' }}>
                        New Patients
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <TrendingUp sx={{ color: '#4CAF50', fontSize: 16 }} />
                    <Typography variant="caption" sx={{ color: '#4CAF50', fontWeight: 600 }}>
                      {stats.new_patients_percent || 0}%
                    </Typography>
                  </Box>
                </Box>

                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: '#FFF3E0',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <People sx={{ color: '#FF9800', fontSize: 24 }} />
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: '#333' }}>
                        {formatNumber(stats.old_patients || 0)}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#666', fontSize: '12px' }}>
                        Old Patients
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <TrendingUp sx={{ color: '#4CAF50', fontSize: 16 }} />
                    <Typography variant="caption" sx={{ color: '#4CAF50', fontWeight: 600 }}>
                      {stats.old_patients_percent || 0}%
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {/* Donut Chart */}
              <Box sx={{ position: 'relative', height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#333' }}>
                    {stats.total_patients || 0}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#666' }}>
                    Total
                  </Typography>
                </Box>
              </Box>

              {/* Legend */}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 2 }}>
                {chartData.map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        bgcolor: item.color,
                      }}
                    />
                    <Typography variant="caption" sx={{ color: '#666', fontSize: '12px' }}>
                      {item.name} {demographics[item.name.toLowerCase()]?.percent || 0}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Today Appointments */}
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              height: '100%',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <FormControl size="small" sx={{ minWidth: 80 }}>
                  <Select
                    value={new Date().getFullYear()}
                    sx={{
                      height: 32,
                      fontSize: '12px',
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: '#E0E0E0',
                      },
                    }}
                  >
                    <MenuItem value={new Date().getFullYear()}>{new Date().getFullYear()}</MenuItem>
                  </Select>
                </FormControl>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#333' }}>
                  Today Appointments
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {todayAppointments.length > 0 ? (
                  todayAppointments.map((appointment, index) => (
                    <Box
                      key={appointment.user_id || index}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: '#F5F5F5',
                        '&:hover': { bgcolor: '#EEEEEE' },
                      }}
                    >
                      <Avatar
                        sx={{
                          bgcolor: colors.darkGreen,
                          width: 40,
                          height: 40,
                        }}
                      >
                        {appointment.username?.charAt(0)?.toUpperCase() || 'U'}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#333' }}>
                          {appointment.username || 'Unknown User'}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#666', fontSize: '12px' }}>
                          {appointment.type || 'Consultation'}
                        </Typography>
                      </Box>
                      <Typography
                        variant="caption"
                        sx={{
                          color: appointment.status === 'Ongoing' ? '#FF9800' : '#666',
                          fontWeight: appointment.status === 'Ongoing' ? 600 : 400,
                          fontSize: '12px',
                        }}
                      >
                        {appointment.status === 'Ongoing' ? 'Ongoing' : appointment.time || 'N/A'}
                      </Typography>
                    </Box>
                  ))
                ) : (
                  <Typography variant="body2" sx={{ color: '#999', textAlign: 'center', py: 3 }}>
                    No appointments today
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
