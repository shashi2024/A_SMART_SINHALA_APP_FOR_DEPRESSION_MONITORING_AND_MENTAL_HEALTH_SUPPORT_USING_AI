import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Chip,
  CircularProgress,
} from '@mui/material';

function Dashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      setUsers(response.data.users);
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

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
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
        Admin Dashboard
      </Typography>

      <Card style={{ marginBottom: 20 }}>
        <CardContent>
          <Typography variant="h6">Summary</Typography>
          <Typography>Total Users: {users.length}</Typography>
          <Typography>
            High Risk Users:{' '}
            {users.filter((u) => u.risk_level === 'high' || u.risk_level === 'severe').length}
          </Typography>
        </CardContent>
      </Card>

      <TableContainer component={Paper}>
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
            {users.map((user) => (
              <TableRow
                key={user.user_id}
                hover
                onClick={() => navigate(`/users/${user.user_id}`)}
                style={{ cursor: 'pointer' }}
              >
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.total_sessions}</TableCell>
                <TableCell>
                  {user.average_depression_score
                    ? (user.average_depression_score * 100).toFixed(1) + '%'
                    : 'N/A'}
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.risk_level || 'low'}
                    color={getRiskColor(user.risk_level)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(user.last_activity).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/digital-twin/${user.user_id}`);
                    }}
                  >
                    View Digital Twin
                  </button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

export default Dashboard;

