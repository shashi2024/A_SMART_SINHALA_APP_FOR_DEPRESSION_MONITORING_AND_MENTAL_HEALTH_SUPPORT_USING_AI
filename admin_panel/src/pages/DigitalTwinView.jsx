import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import {
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Grid,
  Chip,
} from '@mui/material';

function DigitalTwinView() {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [riskFactors, setRiskFactors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDigitalTwin();
  }, [userId]);

  const loadDigitalTwin = async () => {
    try {
      const response = await api.get(`/admin/users/${userId}/profile`);
      const twinData = response.data.digital_twin;
      
      if (twinData) {
        setProfile(JSON.parse(twinData.mental_health_profile));
        setRiskFactors(JSON.parse(twinData.risk_factors));
      }
    } catch (error) {
      console.error('Failed to load digital twin:', error);
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

  return (
    <div style={{ padding: 20 }}>
      <Typography variant="h4" gutterBottom>
        Digital Twin Profile - User {userId}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Mental Health Profile
              </Typography>
              {profile ? (
                <>
                  <Typography>
                    Total Sessions: {profile.total_sessions || 0}
                  </Typography>
                  <Typography>
                    Average Depression Score:{' '}
                    {profile.average_depression_score
                      ? (profile.average_depression_score * 100).toFixed(1) + '%'
                      : 'N/A'}
                  </Typography>
                  <Typography>
                    Risk Level:{' '}
                    <Chip
                      label={profile.risk_level || 'low'}
                      color={
                        profile.risk_level === 'severe' || profile.risk_level === 'high'
                          ? 'error'
                          : 'success'
                      }
                      size="small"
                    />
                  </Typography>
                </>
              ) : (
                <Typography>No profile data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Factors
              </Typography>
              {riskFactors && riskFactors.length > 0 ? (
                <ul>
                  {riskFactors.map((factor, index) => (
                    <li key={index}>{factor}</li>
                  ))}
                </ul>
              ) : (
                <Typography>No significant risk factors detected</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
}

export default DigitalTwinView;

