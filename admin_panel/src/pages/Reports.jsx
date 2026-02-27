import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Download as DownloadIcon,
  DateRange as DateRangeIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

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

function Reports() {
  const [loading, setLoading] = useState(true);
  const [reportType, setReportType] = useState('weekly');
  const [dashboardData, setDashboardData] = useState(null);
  const [moodData, setMoodData] = useState(null);

  useEffect(() => {
    loadReportData();
  }, [reportType]);

  const loadReportData = async () => {
    setLoading(true);
    try {
      // Load dashboard data for statistics
      const dashboardResponse = await api.get('/admin/dashboard');
      setDashboardData(dashboardResponse.data.users || []);

      // Load mood check-ins
      const moodResponse = await api.get('/admin/mood-checkins', {
        params: {
          limit: 200,
        },
      });
      setMoodData(moodResponse.data.checkins || []);

    } catch (error) {
      console.error('Failed to load report data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateRiskDistribution = () => {
    if (!dashboardData) return [];
    
    const distribution = {
      severe: 0,
      high: 0,
      moderate: 0,
      low: 0,
    };

    dashboardData.forEach((user) => {
      const risk = user.risk_level?.toLowerCase() || 'low';
      if (distribution.hasOwnProperty(risk)) {
        distribution[risk]++;
      } else {
        distribution.low++;
      }
    });

    return [
      { name: 'Severe', value: distribution.severe, color: colors.red },
      { name: 'High', value: distribution.high, color: colors.orange },
      { name: 'Moderate', value: distribution.moderate, color: colors.blue },
      { name: 'Low', value: distribution.low, color: colors.darkGreen },
    ];
  };

  const generateMoodTrendData = () => {
    if (!moodData || moodData.length === 0) return [];

    // Group by date
    const moodByDate = {};
    moodData.forEach((checkin) => {
      const date = checkin.date || checkin.created_at?.split('T')[0] || 'Unknown';
      if (!moodByDate[date]) {
        moodByDate[date] = { date, Excited: 0, Happy: 0, Calm: 0, Neutral: 0, Anxious: 0, Sad: 0 };
      }
      const mood = checkin.mood;
      if (moodByDate[date].hasOwnProperty(mood)) {
        moodByDate[date][mood]++;
      }
    });

    return Object.values(moodByDate).sort((a, b) => a.date.localeCompare(b.date));
  };

  const handleExport = () => {
    // Generate CSV export
    if (!dashboardData) return;

    const headers = ['Username', 'Email', 'Total Sessions', 'Average Depression Score', 'Risk Level', 'Last Activity'];
    const rows = dashboardData.map((user) => [
      user.username,
      user.email,
      user.total_sessions,
      user.average_depression_score?.toFixed(2) || 'N/A',
      user.risk_level,
      user.last_activity ? new Date(user.last_activity).toLocaleString() : 'N/A',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `depression-monitoring-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </Box>
    );
  }

  const riskDistribution = generateRiskDistribution();
  const moodTrend = generateMoodTrendData();

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Reports & Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Report Period</InputLabel>
            <Select
              value={reportType}
              label="Report Period"
              onChange={(e) => setReportType(e.target.value)}
            >
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
            sx={{
              bgcolor: colors.darkGreen,
              '&:hover': { bgcolor: '#134030' },
            }}
          >
            Export Report
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Risk Level Distribution */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Risk Level Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={riskDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill={colors.darkGreen} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Mood Trends */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Mood Trends Over Time
              </Typography>
              {moodTrend.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={moodTrend.slice(-7)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Happy" stroke={colors.darkGreen} />
                    <Line type="monotone" dataKey="Sad" stroke={colors.red} />
                    <Line type="monotone" dataKey="Anxious" stroke={colors.orange} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Typography textAlign="center" color="text.secondary" sx={{ mt: 10 }}>
                  No mood data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Summary Statistics */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
                Summary Statistics
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.veryLightBlue, borderRadius: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                      {dashboardData?.length || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Patients
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.paleSageGreen, borderRadius: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                      {dashboardData?.filter((u) => u.risk_level === 'low' || !u.risk_level).length || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Low Risk
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.lightPeach, borderRadius: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                      {dashboardData?.filter((u) => ['high', 'severe'].includes(u.risk_level?.toLowerCase())).length || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      High Risk
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.creamYellow, borderRadius: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                      {moodData?.length || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Mood Check-ins
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Reports;

