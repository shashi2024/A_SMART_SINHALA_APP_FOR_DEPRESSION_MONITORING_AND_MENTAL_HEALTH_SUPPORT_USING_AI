import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Avatar,
  Button,
  Chip,
  CircularProgress,
  Paper,
} from '@mui/material';
import {
  CalendarToday,
  People,
  Description,
  Videocam,
  TrendingUp,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

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

function Dashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [appointments, setAppointments] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      setUsers(response.data.users || []);
      
      // Generate sample appointment data
      setAppointments([
        { id: 1, name: 'Bogdan Krivenchenko', details: '45 Male, 12 April 9:30', status: 'pending' },
        { id: 2, name: 'John Doe', details: '32 Female, 12 April 10:00', status: 'confirmed' },
        { id: 3, name: 'Jane Smith', details: '28 Male, 12 April 11:00', status: 'declined' },
        { id: 4, name: 'Mike Johnson', details: '35 Female, 12 April 14:00', status: 'confirmed' },
        { id: 5, name: 'Sarah Williams', details: '40 Male, 12 April 15:30', status: 'pending' },
      ]);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'severe':
      case 'high':
        return colors.red;
      case 'moderate':
        return colors.orange;
      default:
        return colors.darkGreen;
    }
  };

  // Calculate statistics
  const totalUsers = users.length;
  const highRiskUsers = users.filter((u) => u.risk_level === 'high' || u.risk_level === 'severe').length;
  const midRiskUsers = users.filter((u) => u.risk_level === 'moderate').length;
  const lowRiskUsers = users.filter((u) => u.risk_level === 'low' || !u.risk_level).length;

  // Patient demographics data for donut chart
  const demographicsData = [
    { name: 'Male', value: 45, color: colors.orange },
    { name: 'Female', value: 45, color: colors.purple },
    { name: 'Child', value: 45, color: colors.blue },
  ];

  // Today's appointments
  const todayAppointments = [
    { id: 1, name: 'Jhon Smith', type: 'Clinic Consulting', time: 'Ongoing' },
    { id: 2, name: 'Mary Johnson', type: 'Vedio Consulting', time: '10.25' },
    { id: 3, name: 'David Brown', type: 'Emergency', time: '11.30' },
    { id: 4, name: 'Emily Davis', type: 'Clinic Consulting', time: '12.20' },
    { id: 5, name: 'Robert Wilson', type: 'Vedio Consulting', time: 'Ongoing' },
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.purple,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    24.4k
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Appointments
                  </Typography>
                </Box>
                <CalendarToday sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.red,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    166.3k
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Total Patients
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.orange,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    53.5k
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Clinic Consulting
                  </Typography>
                </Box>
                <Description sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.blue,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    28.0k
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Video Consulting
                  </Typography>
                </Box>
                <Videocam sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content - Three Columns */}
      <Grid container spacing={3}>
        {/* Left Column - Appointment Requests */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              borderRadius: 3,
              bgcolor: 'white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              Appointment Request
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {appointments.map((appointment) => (
                <Box
                  key={appointment.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    p: 2,
                    borderRadius: 2,
                    bgcolor: '#F9F9F9',
                  }}
                >
                  <Avatar sx={{ bgcolor: colors.darkGreen }}>
                    {appointment.name.charAt(0)}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {appointment.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>
                      {appointment.details}
                    </Typography>
                  </Box>
                  <Button
                    size="small"
                    variant="contained"
                    sx={{
                      bgcolor:
                        appointment.status === 'confirmed'
                          ? colors.blue
                          : appointment.status === 'declined'
                          ? colors.red
                          : colors.orange,
                      color: 'white',
                      textTransform: 'none',
                      borderRadius: 2,
                      px: 2,
                    }}
                  >
                    {appointment.status === 'confirmed'
                      ? 'Confirmed'
                      : appointment.status === 'declined'
                      ? 'Declined'
                      : 'Pending'}
                  </Button>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Middle Column - Patients */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              borderRadius: 3,
              bgcolor: 'white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                patients
              </Typography>
              <Typography
                variant="body2"
                sx={{ color: colors.darkGreen, cursor: 'pointer', textDecoration: 'underline' }}
              >
                View All
              </Typography>
            </Box>

            {/* Patient Counts */}
            <Box sx={{ mb: 3 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  p: 2,
                  borderRadius: 2,
                  bgcolor: colors.veryLightBlue,
                  mb: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <People sx={{ color: colors.blue, fontSize: 32 }} />
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                      24.4k
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#666' }}>
                      New Patients
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <TrendingUp sx={{ color: colors.darkGreen }} />
                  <Typography variant="body2" sx={{ color: colors.darkGreen, fontWeight: 600 }}>
                    15%
                  </Typography>
                </Box>
              </Box>

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  p: 2,
                  borderRadius: 2,
                  bgcolor: colors.lightPeach,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <People sx={{ color: colors.orange, fontSize: 32 }} />
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                      166.3k
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#666' }}>
                      Old Patients
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <TrendingUp sx={{ color: colors.darkGreen }} />
                  <Typography variant="body2" sx={{ color: colors.darkGreen, fontWeight: 600 }}>
                    15%
                  </Typography>
                </Box>
              </Box>
            </Box>

            {/* Donut Chart */}
            <Box>
              <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
                Patient Demographics
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={demographicsData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {demographicsData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend
                    verticalAlign="middle"
                    align="right"
                    layout="vertical"
                    iconType="circle"
                  />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Right Column - Today Appointments */}
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 3,
              borderRadius: 3,
              bgcolor: 'white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="body2" sx={{ color: '#666' }}>
                2025 ▼
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Today Appointments
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {todayAppointments.map((appointment) => (
                <Box
                  key={appointment.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    p: 2,
                    borderRadius: 2,
                    bgcolor: '#F9F9F9',
                  }}
                >
                  <Avatar sx={{ bgcolor: colors.darkGreen }}>
                    {appointment.name.charAt(0)}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {appointment.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>
                      {appointment.type}
                    </Typography>
                  </Box>
                  <Chip
                    label={appointment.time}
                    size="small"
                    sx={{
                      bgcolor:
                        appointment.time === 'Ongoing' ? colors.darkGreen : 'transparent',
                      color: appointment.time === 'Ongoing' ? 'white' : '#666',
                      fontWeight: 600,
                    }}
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
