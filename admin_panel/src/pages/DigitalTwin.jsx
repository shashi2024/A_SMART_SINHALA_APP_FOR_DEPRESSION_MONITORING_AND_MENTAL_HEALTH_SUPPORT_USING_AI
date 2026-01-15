import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
};

function DigitalTwin() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

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
    switch (riskLevel?.toLowerCase()) {
      case 'severe':
        return 'error';
      case 'high':
        return 'warning';
      case 'moderate':
        return 'info';
      default:
        return 'success';
    }
  };

  const filteredUsers = users.filter(
    (user) =>
      user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Digital Twin - Mental Health Profiles
        </Typography>
        <TextField
          placeholder="Search users..."
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, bgcolor: colors.darkGreen, color: 'white' }}>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                {users.length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Total Users
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, bgcolor: colors.paleSageGreen }}>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, color: colors.darkGreen }}>
                {users.filter((u) => u.risk_level === 'low' || !u.risk_level).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Low Risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, bgcolor: colors.lightPeach }}>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, color: colors.darkGreen }}>
                {users.filter((u) => ['high', 'severe'].includes(u.risk_level?.toLowerCase())).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                High Risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, bgcolor: colors.veryLightBlue }}>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, color: colors.darkGreen }}>
                {users.reduce((sum, u) => sum + (u.total_sessions || 0), 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Sessions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Digital Twin Profiles Table */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
                User Digital Twin Profiles
              </Typography>
              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Username</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Total Sessions</TableCell>
                      <TableCell>Avg Depression Score</TableCell>
                      <TableCell>Risk Level</TableCell>
                      <TableCell>Last Activity</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredUsers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          No users found
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredUsers.map((user) => (
                        <TableRow key={user.user_id}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <PersonIcon sx={{ color: colors.darkGreen }} />
                              {user.username}
                            </Box>
                          </TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>{user.total_sessions || 0}</TableCell>
                          <TableCell>
                            {user.average_depression_score
                              ? `${(user.average_depression_score * 100).toFixed(1)}%`
                              : 'N/A'}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={user.risk_level || 'low'}
                              size="small"
                              color={getRiskColor(user.risk_level)}
                            />
                          </TableCell>
                          <TableCell>
                            {user.last_activity
                              ? new Date(user.last_activity).toLocaleString()
                              : 'N/A'}
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              startIcon={<VisibilityIcon />}
                              onClick={() => navigate(`/digital-twin/${user.user_id}`)}
                              sx={{ color: colors.darkGreen }}
                            >
                              View Profile
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DigitalTwin;

