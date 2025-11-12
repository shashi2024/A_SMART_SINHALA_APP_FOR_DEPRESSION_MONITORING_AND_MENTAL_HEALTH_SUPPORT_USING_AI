import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import {
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';

function UserProfile() {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, [userId]);

  const loadProfile = async () => {
    try {
      const response = await api.get(`/admin/users/${userId}/profile`);
      setProfile(response.data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </div>
    );
  }

  if (!profile) {
    return <Typography>User not found</Typography>;
  }

  return (
    <div style={{ padding: 20 }}>
      <Typography variant="h4" gutterBottom>
        User Profile - {profile.user.username}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Information
              </Typography>
              <Typography>Email: {profile.user.email}</Typography>
              <Typography>Phone: {profile.user.phone_number || 'N/A'}</Typography>
              <Typography>
                Created: {new Date(profile.user.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Session History
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Start Time</TableCell>
                      <TableCell>Depression Score</TableCell>
                      <TableCell>Risk Level</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {profile.sessions.map((session) => (
                      <TableRow key={session.id}>
                        <TableCell>{session.type}</TableCell>
                        <TableCell>
                          {new Date(session.start_time).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          {session.depression_score
                            ? (session.depression_score * 100).toFixed(1) + '%'
                            : 'N/A'}
                        </TableCell>
                        <TableCell>{session.risk_level || 'low'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
}

export default UserProfile;

