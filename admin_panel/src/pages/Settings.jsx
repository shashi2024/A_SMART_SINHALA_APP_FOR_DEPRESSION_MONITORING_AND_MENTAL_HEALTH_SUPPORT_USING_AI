import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
};

function Settings() {

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Panel Settings
      </Typography>

      <Box>
            <Grid container spacing={3}>
              {/* Panel Configuration Section */}
              <Grid item xs={12}>
                <Card sx={{ borderRadius: 3, boxShadow: 2, mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                      Panel Configuration
                    </Typography>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <FormControlLabel
                          control={<Switch defaultChecked />}
                          label="Enable Notifications"
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 0.5 }}>
                          Show notification badges and alerts in the panel
                        </Typography>
                      </Grid>
                      <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />
                      <Grid item xs={12} md={5}>
                        <FormControlLabel
                          control={<Switch defaultChecked />}
                          label="Enable Email Alerts"
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 0.5 }}>
                          Send email notifications for critical alerts
                        </Typography>
                      </Grid>
                    </Grid>
                    <Divider sx={{ my: 3 }} />
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <FormControlLabel
                          control={<Switch defaultChecked />}
                          label="Enable Location Tracking"
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 0.5 }}>
                          Track user locations for safety monitoring
                        </Typography>
                      </Grid>
                      <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />
                      <Grid item xs={12} md={5}>
                        <FormControlLabel
                          control={<Switch defaultChecked />}
                          label="Auto-refresh Dashboard"
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 4, mt: 0.5 }}>
                          Automatically refresh dashboard data
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Application Information Section */}
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                      Application Information
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Application Version
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          1.0.0
                        </Typography>
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      <Box sx={{ mb: 3 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          API Endpoint
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          http://localhost:8000/api
                        </Typography>
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      <Box sx={{ mb: 3 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Database
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          Firebase Firestore
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* System Status Section */}
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
                      System Status
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Box
                            sx={{
                              width: 12,
                              height: 12,
                              borderRadius: '50%',
                              bgcolor: '#4CAF50',
                            }}
                          />
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            System Online
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          All services are running normally
                        </Typography>
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Box
                            sx={{
                              width: 12,
                              height: 12,
                              borderRadius: '50%',
                              bgcolor: '#4CAF50',
                            }}
                          />
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            Database Connected
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Firestore connection active
                        </Typography>
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Box
                            sx={{
                              width: 12,
                              height: 12,
                              borderRadius: '50%',
                              bgcolor: '#4CAF50',
                            }}
                          />
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            API Server Running
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Backend API is operational
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
    </Box>
  );
}

export default Settings;

