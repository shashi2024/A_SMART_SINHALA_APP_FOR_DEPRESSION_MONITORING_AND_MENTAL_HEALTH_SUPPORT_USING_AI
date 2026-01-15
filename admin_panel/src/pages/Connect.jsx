import React, { useState, useEffect } from 'react';
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
  IconButton,
} from '@mui/material';
import {
  Phone as PhoneIcon,
  VideoCall as VideoCallIcon,
  Chat as ChatIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
};

function Connect() {
  const [loading, setLoading] = useState(true);
  const [calls, setCalls] = useState([]);
  const [counselors, setCounselors] = useState([]);

  useEffect(() => {
    loadConnectData();
  }, []);

  const loadConnectData = async () => {
    try {
      // Load call history
      const callsResponse = await api.get('/calls/history', {
        params: { limit: 100 },
      });
      setCalls(callsResponse.data.calls || []);

      // Load available counselors
      const counselorsResponse = await api.get('/calls/counselors/available');
      setCounselors(counselorsResponse.data.counselors || []);
    } catch (error) {
      console.error('Failed to load connect data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCallTypeIcon = (callType) => {
    switch (callType?.toLowerCase()) {
      case 'video':
        return <VideoCallIcon />;
      case 'audio':
        return <PhoneIcon />;
      default:
        return <ChatIcon />;
    }
  };

  const getCallTypeColor = (callType) => {
    switch (callType?.toLowerCase()) {
      case 'counselor':
        return colors.darkGreen;
      case 'ai_practice':
        return colors.blue;
      case 'emergency':
        return colors.red;
      default:
        return colors.orange;
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
        Connect - Calls & Communications
      </Typography>

      <Grid container spacing={3}>
        {/* Counselors Section */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, boxShadow: 2, mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Available Counselors
              </Typography>
              {counselors.length === 0 ? (
                <Typography color="text.secondary">No counselors available</Typography>
              ) : (
                <Box sx={{ mt: 2 }}>
                  {counselors.map((counselor) => (
                    <Card
                      key={counselor.id}
                      sx={{
                        mb: 2,
                        p: 2,
                        bgcolor: colors.veryLightBlue,
                        borderRadius: 2,
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {counselor.name || counselor.username}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Languages: {counselor.languages?.join(', ') || 'English'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Rating: {counselor.rating || 'N/A'}
                          </Typography>
                        </Box>
                        <Chip
                          label="Available"
                          color="success"
                          size="small"
                        />
                      </Box>
                    </Card>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Call Statistics */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Call Statistics
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.paleSageGreen, borderRadius: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                      {calls.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Calls
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: colors.lightPeach, borderRadius: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                      {counselors.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active Counselors
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Call History */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Call History
              </Typography>
              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Caller</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Duration</TableCell>
                      <TableCell>Started At</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {calls.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          No calls found
                        </TableCell>
                      </TableRow>
                    ) : (
                      calls.map((call) => (
                        <TableRow key={call.id}>
                          <TableCell>
                            <Chip
                              icon={getCallTypeIcon(call.call_type)}
                              label={call.call_type || 'Unknown'}
                              size="small"
                              sx={{
                                bgcolor: getCallTypeColor(call.call_type),
                                color: 'white',
                              }}
                            />
                          </TableCell>
                          <TableCell>{call.caller_username || 'Unknown'}</TableCell>
                          <TableCell>
                            <Chip
                              label={call.status || 'unknown'}
                              size="small"
                              color={
                                call.status === 'completed'
                                  ? 'success'
                                  : call.status === 'active'
                                  ? 'primary'
                                  : 'default'
                              }
                            />
                          </TableCell>
                          <TableCell>
                            {call.duration
                              ? `${Math.floor(call.duration / 60)}m ${call.duration % 60}s`
                              : 'N/A'}
                          </TableCell>
                          <TableCell>
                            {call.started_at
                              ? new Date(call.started_at).toLocaleString()
                              : 'N/A'}
                          </TableCell>
                          <TableCell>
                            <IconButton size="small">
                              <MoreVertIcon />
                            </IconButton>
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

export default Connect;

