import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  TextField,
  Button,
  Typography,
  InputAdornment,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person,
  Lock,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
  lightPink: '#FFF5F5',
};

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      if (err.message && err.message.includes('Admin privileges')) {
        setError('Access denied: Admin privileges required');
      } else {
        setError('Invalid credentials. Please check your username and password.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: colors.lightPink,
        background: `linear-gradient(135deg, ${colors.veryLightBlue} 0%, ${colors.creamYellow} 100%)`,
        padding: 3,
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: 450,
          bgcolor: 'white',
          borderRadius: 4,
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          padding: 4,
        }}
      >
        {/* Logo Section */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mb: 4,
          }}
        >
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              bgcolor: colors.lightPink,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
              position: 'relative',
            }}
          >
            {/* Logo icon - brain/heart design */}
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                bgcolor: '#9C27B0', // Purple
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
              }}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  bgcolor: colors.darkGreen,
                  position: 'absolute',
                  top: -5,
                  right: -5,
                }}
              />
            </Box>
          </Box>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 'bold',
              color: colors.darkGreen,
              mb: 1,
            }}
          >
            Admin Dashboard
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: '#666',
              textAlign: 'center',
            }}
          >
            Sign in to access the admin panel
          </Typography>
        </Box>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            fullWidth
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
            required
            autoComplete="username"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Person sx={{ color: '#999' }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                bgcolor: '#F9F9F9',
                '& fieldset': {
                  borderColor: '#E0E0E0',
                },
                '&:hover fieldset': {
                  borderColor: colors.darkGreen,
                },
                '&.Mui-focused fieldset': {
                  borderColor: colors.darkGreen,
                },
              },
              mb: 2,
            }}
          />

          <TextField
            fullWidth
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
            autoComplete="current-password"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock sx={{ color: '#999' }} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                    sx={{ color: '#999' }}
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                bgcolor: '#F9F9F9',
                '& fieldset': {
                  borderColor: '#E0E0E0',
                },
                '&:hover fieldset': {
                  borderColor: colors.darkGreen,
                },
                '&.Mui-focused fieldset': {
                  borderColor: colors.darkGreen,
                },
              },
              mb: 3,
            }}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={loading}
            sx={{
              bgcolor: colors.darkGreen,
              color: 'white',
              padding: 1.5,
              borderRadius: 2,
              fontSize: '16px',
              fontWeight: 600,
              textTransform: 'none',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
              '&:hover': {
                bgcolor: '#134738',
                boxShadow: '0 6px 8px rgba(0,0,0,0.15)',
              },
              '&:disabled': {
                bgcolor: colors.darkGreen,
                opacity: 0.7,
              },
            }}
          >
            {loading ? (
              <CircularProgress size={24} sx={{ color: 'white' }} />
            ) : (
              'Sign In'
            )}
          </Button>
        </form>

        {/* Footer */}
        <Box
          sx={{
            mt: 4,
            textAlign: 'center',
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: '#999',
              fontSize: '12px',
            }}
          >
            Depression Monitoring System - Admin Panel
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

export default Login;
