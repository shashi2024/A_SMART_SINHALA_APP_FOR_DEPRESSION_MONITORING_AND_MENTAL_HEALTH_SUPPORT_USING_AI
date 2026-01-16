import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  CalendarToday,
  People,
  Description,
  Videocam,
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

function PatientsRiskLevel() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Failed to load users:', error);
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

  // Calculate statistics
  const totalUsers = users.length;
  const highRiskUsers = users.filter((u) => u.risk_level === 'high' || u.risk_level === 'severe').length;
  const midRiskUsers = users.filter((u) => u.risk_level === 'moderate').length;
  const lowRiskUsers = users.filter((u) => u.risk_level === 'low' || !u.risk_level).length;

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
        Patients Risk Level
      </Typography>

      {/* Statistics Cards123*/}
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
                    {totalUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Total Users
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
                    {highRiskUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    High Risk Users
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
                    {midRiskUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Mid Risk Users
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
                    {lowRiskUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Low Risk Users
                  </Typography>
                </Box>
                <Videocam sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Patients Table */}
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
              <TableCell sx={{ fontWeight: 'bold' }}>Username</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Email</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Total Sessions</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Risk Level</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Last Activity</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    No users found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow
                  key={user.user_id}
                  hover
                  onClick={() => navigate(`/users/${user.user_id}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{user.username || 'N/A'}</TableCell>
                  <TableCell>{user.email || 'N/A'}</TableCell>
                  <TableCell>{user.total_sessions || '01'}</TableCell>
                  <TableCell>
                    <Chip
                      label={getRiskLabel(user.risk_level)}
                      size="small"
                      sx={{
                        bgcolor: getRiskColor(user.risk_level),
                        color: 'white',
                        fontWeight: 600,
                        borderRadius: 2,
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    {user.last_activity
                      ? new Date(user.last_activity).toLocaleDateString()
                      : '10/29/2025'}
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

export default PatientsRiskLevel;



























