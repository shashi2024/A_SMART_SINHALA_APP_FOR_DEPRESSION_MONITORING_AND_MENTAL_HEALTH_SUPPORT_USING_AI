import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';
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
  IconButton,
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Map as MapIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
};

function LocationTracking() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    loadLocationData();
  }, []);

  const loadLocationData = async () => {
    try {
      // Load users for location tracking
      const usersResponse = await api.get('/admin/dashboard');
      setUsers(usersResponse.data.users || []);

      // Load location data (if available)
      // Note: This assumes location tracking data exists
      // For now, we'll show users with their last activity as location data
      setLocations(
        (usersResponse.data.users || []).map((user) => ({
          user_id: user.user_id,
          username: user.username,
          email: user.email,
          last_location: 'Not tracked',
          last_activity: user.last_activity,
          status: 'offline',
        }))
      );
    } catch (error) {
      console.error('Failed to load location data:', error);
    } finally {
      setLoading(false);
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Location Tracking
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadLocationData}
          sx={{ borderColor: colors.darkGreen, color: colors.darkGreen }}
        >
          Refresh
        </Button>
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
                {locations.filter((l) => l.status === 'online').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Users
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, bgcolor: colors.lightPeach }}>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, color: colors.darkGreen }}>
                {locations.filter((l) => l.last_location !== 'Not tracked').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tracked Locations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, bgcolor: colors.veryLightBlue }}>
            <CardContent>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, color: colors.darkGreen }}>
                {new Date().toLocaleDateString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Today
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Location Tracking Table */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <MapIcon sx={{ color: colors.darkGreen }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  User Locations
                </Typography>
              </Box>
              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Username</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Last Location</TableCell>
                      <TableCell>Last Activity</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {locations.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          No location data available
                        </TableCell>
                      </TableRow>
                    ) : (
                      locations.map((location) => (
                        <TableRow key={location.user_id}>
                          <TableCell>{location.username}</TableCell>
                          <TableCell>{location.email}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <LocationIcon sx={{ color: colors.darkGreen, fontSize: 20 }} />
                              {location.last_location}
                            </Box>
                          </TableCell>
                          <TableCell>
                            {location.last_activity
                              ? new Date(location.last_activity).toLocaleString()
                              : 'N/A'}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={location.status}
                              size="small"
                              color={location.status === 'online' ? 'success' : 'default'}
                            />
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              onClick={() => navigate(`/users/${location.user_id}`)}
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

        {/* Map Placeholder */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Location Map
              </Typography>
              <Box
                sx={{
                  height: 350,
                  bgcolor: colors.veryLightBlue,
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mt: 2,
                }}
              >
                <Typography color="text.secondary">
                  Map view will be displayed here (integrate with Google Maps or similar)
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default LocationTracking;

