import React, { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api';
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
  Alert,
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

// Google Maps API Key - Replace with your own API key
// Get one from: https://console.cloud.google.com/google/maps-apis
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

// Default map center (Sri Lanka)
const DEFAULT_CENTER = { lat: 7.8731, lng: 80.7718 };
const DEFAULT_ZOOM = 7;

// Map container style
const mapContainerStyle = {
  width: '100%',
  height: '350px',
};

function LocationTracking() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);

  useEffect(() => {
    loadLocationData();
  }, []);

  const loadLocationData = async () => {
    try {
      // Load location data from location API
      const locationsResponse = await api.get('/location/all');
      const locationsData = locationsResponse.data.locations || [];
      
      setLocations(locationsData.map((loc) => ({
        user_id: loc.user_id,
        username: loc.username,
        email: loc.email,
        phone_number: loc.phone_number,
        latitude: loc.latitude,
        longitude: loc.longitude,
        last_location: loc.latitude && loc.longitude 
          ? `${loc.latitude.toFixed(6)}, ${loc.longitude.toFixed(6)}`
          : 'Not tracked',
        last_activity: loc.last_updated,
        status: loc.last_updated ? 'online' : 'offline',
        accuracy: loc.accuracy,
      })));
      
      setUsers(locationsData);
    } catch (error) {
      console.error('Failed to load location data:', error);
      setLocations([]);
    } finally {
      setLoading(false);
    }
  };

  // Calculate map center based on locations
  const mapCenter = useMemo(() => {
    const validLocations = locations.filter(loc => loc.latitude && loc.longitude);
    if (validLocations.length === 0) {
      return DEFAULT_CENTER;
    }
    
    if (validLocations.length === 1) {
      return { lat: validLocations[0].latitude, lng: validLocations[0].longitude };
    }
    
    // Calculate center point of all locations
    const avgLat = validLocations.reduce((sum, loc) => sum + loc.latitude, 0) / validLocations.length;
    const avgLng = validLocations.reduce((sum, loc) => sum + loc.longitude, 0) / validLocations.length;
    return { lat: avgLat, lng: avgLng };
  }, [locations]);

  // Filter valid locations for markers
  const validLocations = locations.filter(loc => loc.latitude && loc.longitude);

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
                      <TableCell>Phone Number</TableCell>
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
                          <TableCell>
                            {location.phone_number || 'N/A'}
                          </TableCell>
                          <TableCell>{location.email}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <LocationIcon sx={{ color: colors.darkGreen, fontSize: 20 }} />
                              {location.last_location}
                              {location.latitude && location.longitude && (
                                <Button
                                  size="small"
                                  onClick={() => {
                                    const url = `https://www.google.com/maps?q=${location.latitude},${location.longitude}`;
                                    window.open(url, '_blank');
                                  }}
                                  sx={{ ml: 1, fontSize: '0.7rem', minWidth: 'auto', p: 0.5 }}
                                >
                                  View Map
                                </Button>
                              )}
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

        {/* Location Map */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, height: 400 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Location Map
              </Typography>
              {!GOOGLE_MAPS_API_KEY ? (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Google Maps API key not configured. Please set VITE_GOOGLE_MAPS_API_KEY in your .env file.
                  <br />
                  Get your API key from: <a href="https://console.cloud.google.com/google/maps-apis" target="_blank" rel="noopener noreferrer">Google Cloud Console</a>
                </Alert>
              ) : (
                <Box sx={{ mt: 2, borderRadius: 2, overflow: 'hidden' }}>
                  <LoadScript googleMapsApiKey={GOOGLE_MAPS_API_KEY}>
                    <GoogleMap
                      mapContainerStyle={mapContainerStyle}
                      center={mapCenter}
                      zoom={validLocations.length > 1 ? 10 : 15}
                    >
                      {validLocations.map((location, index) => (
                        <Marker
                          key={location.user_id || index}
                          position={{ lat: location.latitude, lng: location.longitude }}
                          onClick={() => setSelectedLocation(location)}
                          label={{
                            text: location.username?.charAt(0).toUpperCase() || 'U',
                            color: 'white',
                            fontWeight: 'bold',
                          }}
                        />
                      ))}
                      {selectedLocation && (
                        <InfoWindow
                          position={{
                            lat: selectedLocation.latitude,
                            lng: selectedLocation.longitude,
                          }}
                          onCloseClick={() => setSelectedLocation(null)}
                        >
                          <div style={{ padding: '4px', minWidth: '200px' }}>
                            <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 'bold' }}>
                              {selectedLocation.username}
                            </h3>
                            <p style={{ margin: '4px 0', fontSize: '12px' }}>
                              <strong>Phone:</strong> {selectedLocation.phone_number || 'N/A'}
                            </p>
                            <p style={{ margin: '4px 0', fontSize: '12px' }}>
                              <strong>Email:</strong> {selectedLocation.email}
                            </p>
                            <p style={{ margin: '4px 0', fontSize: '12px' }}>
                              <strong>Last Activity:</strong>{' '}
                              {selectedLocation.last_activity
                                ? new Date(selectedLocation.last_activity).toLocaleString()
                                : 'N/A'}
                            </p>
                            <span
                              style={{
                                display: 'inline-block',
                                marginTop: '4px',
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontSize: '11px',
                                backgroundColor: selectedLocation.status === 'online' ? '#4caf50' : '#9e9e9e',
                                color: 'white',
                                fontWeight: 'bold',
                              }}
                            >
                              {selectedLocation.status}
                            </span>
                          </div>
                        </InfoWindow>
                      )}
                    </GoogleMap>
                  </LoadScript>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default LocationTracking;

