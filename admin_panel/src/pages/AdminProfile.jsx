import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  TextField,
  Button,
  Avatar,
  Divider,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
};

function AdminProfile() {
  const { user, checkAdminStatus } = useAuth();
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone_number: '',
  });
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await api.get('/auth/me');
      const userInfo = response.data;
      setProfile(userInfo);
      setFormData({
        username: userInfo.username || '',
        email: userInfo.email || '',
        phone_number: userInfo.phone_number || '',
      });
      await checkAdminStatus(); // Refresh user info
    } catch (error) {
      console.error('Failed to load profile:', error);
      setMessage({ type: 'error', text: 'Failed to load profile' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      // Update profile (assuming there's an endpoint)
      await api.put('/auth/profile', formData);
      setMessage({ type: 'success', text: 'Profile updated successfully' });
      setIsEditing(false);
      await loadProfile();
    } catch (error) {
      console.error('Failed to update profile:', error);
      setMessage({ type: 'error', text: 'Failed to update profile' });
    }
  };

  const handleCancel = () => {
    setFormData({
      username: profile?.username || '',
      email: profile?.email || '',
      phone_number: profile?.phone_number || '',
    });
    setIsEditing(false);
    setMessage({ type: '', text: '' });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </Box>
    );
  }

  const displayUser = user || profile;
  const displayName = displayUser?.username || displayUser?.email?.split('@')[0] || 'Admin';

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        My Profile
      </Typography>

      {message.text && (
        <Alert
          severity={message.type === 'error' ? 'error' : 'success'}
          onClose={() => setMessage({ type: '', text: '' })}
          sx={{ mb: 3 }}
        >
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Profile Information
                </Typography>
                {!isEditing ? (
                  <Button
                    startIcon={<EditIcon />}
                    onClick={() => setIsEditing(true)}
                    sx={{ color: colors.darkGreen }}
                  >
                    Edit
                  </Button>
                ) : (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      startIcon={<SaveIcon />}
                      onClick={handleSave}
                      variant="contained"
                      sx={{ bgcolor: colors.darkGreen, '&:hover': { bgcolor: '#134030' } }}
                    >
                      Save
                    </Button>
                    <Button
                      startIcon={<CancelIcon />}
                      onClick={handleCancel}
                      variant="outlined"
                    >
                      Cancel
                    </Button>
                  </Box>
                )}
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
                <Avatar
                  sx={{
                    width: 100,
                    height: 100,
                    bgcolor: colors.darkGreen,
                    fontSize: '3rem',
                    mb: 2,
                  }}
                >
                  {displayName.charAt(0).toUpperCase()}
                </Avatar>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {displayName}
                </Typography>
                {displayUser?.is_admin && (
                  <Typography variant="body2" color="text.secondary">
                    Administrator
                  </Typography>
                )}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    label="Username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    fullWidth
                    disabled={!isEditing}
                    variant={isEditing ? 'outlined' : 'filled'}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    fullWidth
                    disabled={!isEditing}
                    variant={isEditing ? 'outlined' : 'filled'}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Phone Number"
                    value={formData.phone_number || ''}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    fullWidth
                    disabled={!isEditing}
                    variant={isEditing ? 'outlined' : 'filled'}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Account Type"
                    value={displayUser?.is_admin ? 'Administrator' : 'User'}
                    fullWidth
                    disabled
                    variant="filled"
                  />
                </Grid>
                {displayUser?.created_at && (
                  <Grid item xs={12}>
                    <TextField
                      label="Account Created"
                      value={new Date(displayUser.created_at).toLocaleDateString()}
                      fullWidth
                      disabled
                      variant="filled"
                    />
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Account Statistics
              </Typography>
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  User ID
                </Typography>
                <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
                  {displayUser?.id || 'N/A'}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Admin Status
                </Typography>
                <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
                  {displayUser?.is_admin ? 'Administrator' : 'Standard User'}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last Login
                </Typography>
                <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
                  {displayUser?.last_login ? new Date(displayUser.last_login).toLocaleString() : 'N/A'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default AdminProfile;

