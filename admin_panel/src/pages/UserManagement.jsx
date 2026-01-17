import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  TextField,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  InputAdornment,
  Grid,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  PersonAdd as PersonAddIcon,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
};

function UserManagement() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [adminUsers, setAdminUsers] = useState([]);
  const [showPassword, setShowPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    phone_number: '',
    is_admin: false,
    is_sub_admin: false,
    role: '',
    specialization: '',
  });

  const [editFormData, setEditFormData] = useState({
    username: '',
    email: '',
    phone_number: '',
    is_admin: false,
    is_sub_admin: false,
    role: '',
    specialization: '',
  });

  useEffect(() => {
    // Check if user is full admin (not sub-admin)
    if (!user?.is_admin) {
      // Redirect to dashboard if not full admin
      navigate('/dashboard');
      return;
    }
    loadAdminUsers();
  }, [user, navigate]);

  const loadAdminUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get('/admin/users');
      // Get all users (admin, sub-admin, doctors, nurses)
      const allUsers = response.data.users || [];
      // Sort by created_at descending
      allUsers.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return dateB - dateA;
      });
      setAdminUsers(allUsers);
    } catch (error) {
      console.error('Failed to load admin users:', error);
      setMessage({ type: 'error', text: 'Failed to load users' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    if (!formData.username || !formData.email || !formData.password) {
      setMessage({ type: 'error', text: 'Please fill in all required fields' });
      return;
    }

    setLoading(true);
    try {
      await api.post('/admin/users/create', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        phone_number: formData.phone_number || undefined,
        is_admin: formData.is_admin,
        is_sub_admin: formData.is_sub_admin,
        role: formData.role || undefined,
        specialization: formData.role === 'doctor' && formData.specialization ? formData.specialization : undefined,
      });

      setMessage({ type: 'success', text: 'User created successfully' });
      setOpenDialog(false);
      setShowPassword(false);
      setFormData({
        username: '',
        email: '',
        password: '',
        phone_number: '',
        is_admin: false,
        is_sub_admin: false,
        role: '',
        specialization: '',
      });
      await loadAdminUsers();
    } catch (error) {
      console.error('Failed to create user:', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to create user',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEditUser = (adminUser) => {
    setEditingUser(adminUser);
    setEditFormData({
      username: adminUser.username || '',
      email: adminUser.email || '',
      phone_number: adminUser.phone_number || '',
      is_admin: adminUser.is_admin || false,
      is_sub_admin: adminUser.is_sub_admin || false,
      role: adminUser.role || '',
      specialization: adminUser.specialization || '',
    });
    setOpenEditDialog(true);
  };

  const handleUpdateUser = async () => {
    if (!editingUser) return;

    if (!editFormData.username || !editFormData.email) {
      setMessage({ type: 'error', text: 'Username and email are required' });
      return;
    }

    setLoading(true);
    try {
      const userId = editingUser.document_id || editingUser.id || editingUser.user_id;
      if (!userId) {
        setMessage({ type: 'error', text: 'Invalid user ID' });
        setLoading(false);
        return;
      }
      
      await api.put(`/admin/users/${userId}`, {
        username: editFormData.username,
        email: editFormData.email,
        phone_number: editFormData.phone_number || undefined,
        role: editFormData.role || undefined,
        specialization: editFormData.role === 'doctor' && editFormData.specialization ? editFormData.specialization : undefined,
        is_sub_admin: editFormData.is_sub_admin,
        is_admin: editFormData.is_admin,
      });

      setMessage({ type: 'success', text: 'User updated successfully' });
      setOpenEditDialog(false);
      setEditingUser(null);
      setEditFormData({
        username: '',
        email: '',
        phone_number: '',
        is_admin: false,
        is_sub_admin: false,
        role: '',
        specialization: '',
      });
      await loadAdminUsers();
    } catch (error) {
      console.error('Failed to update user:', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to update user',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!user?.is_admin) {
      setMessage({ type: 'error', text: 'Only full administrators can delete users' });
      return;
    }

    if (!userId) {
      setMessage({ type: 'error', text: 'Invalid user ID' });
      return;
    }

    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await api.delete(`/admin/users/${userId}`);
      setMessage({ type: 'success', text: response.data?.message || 'User deleted successfully' });
      setTimeout(() => {
        loadAdminUsers();
      }, 500);
    } catch (error) {
      console.error('Failed to delete user:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete user';
      setMessage({
        type: 'error',
        text: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({
      username: '',
      email: '',
      password: '',
      phone_number: '',
      is_admin: false,
      is_sub_admin: false,
      role: '',
      specialization: '',
    });
    setShowPassword(false);
    setMessage({ type: '', text: '' });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        User Management
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

      <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Users (Admin, Sub-Admin, Doctors & Nurses)
            </Typography>
            {user?.is_admin && (
              <Button
                variant="contained"
                startIcon={<PersonAddIcon />}
                onClick={() => setOpenDialog(true)}
                sx={{
                  bgcolor: colors.darkGreen,
                  '&:hover': { bgcolor: '#134030' },
                }}
              >
                Create User
              </Button>
            )}
            {!user?.is_admin && user?.is_sub_admin && (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                Sub-admins cannot create users. Only full administrators can create users.
              </Typography>
            )}
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', padding: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Username</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Phone</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Specialization</TableCell>
                    <TableCell>Admin Role</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {adminUsers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        No users found
                      </TableCell>
                    </TableRow>
                  ) : (
                    adminUsers
                      .filter((u) => {
                        return u.is_admin || u.is_sub_admin || u.role === 'doctor' || u.role === 'nurse';
                      })
                      .map((adminUser) => {
                        const userId = adminUser.document_id || adminUser.id || adminUser.user_id;
                        return (
                          <TableRow key={userId}>
                            <TableCell>{adminUser.username}</TableCell>
                            <TableCell>{adminUser.email}</TableCell>
                            <TableCell>{adminUser.phone_number || 'N/A'}</TableCell>
                            <TableCell>
                              {adminUser.role ? (
                                <Chip
                                  label={adminUser.role.charAt(0).toUpperCase() + adminUser.role.slice(1)}
                                  size="small"
                                  color={adminUser.role === 'doctor' ? 'primary' : 'info'}
                                />
                              ) : (
                                'N/A'
                              )}
                            </TableCell>
                            <TableCell>
                              {adminUser.specialization || 'N/A'}
                            </TableCell>
                            <TableCell>
                              {adminUser.is_admin ? (
                                <Chip label="Administrator" size="small" color="error" />
                              ) : adminUser.is_sub_admin ? (
                                <Chip label="Sub-Admin" size="small" color="warning" />
                              ) : (
                                <Chip label="User" size="small" color="default" />
                              )}
                            </TableCell>
                            <TableCell>
                              {adminUser.created_at
                                ? new Date(adminUser.created_at).toLocaleDateString()
                                : 'N/A'}
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', gap: 1 }}>
                                {user?.is_admin && (
                                  <IconButton
                                    size="small"
                                    color="primary"
                                    onClick={() => handleEditUser(adminUser)}
                                    title="Edit User"
                                  >
                                    <EditIcon />
                                  </IconButton>
                                )}
                                {userId !== (user?.id || user?.document_id) && user?.is_admin && (
                                  <IconButton
                                    size="small"
                                    color="error"
                                    onClick={() => handleDeleteUser(userId)}
                                    title="Delete User"
                                  >
                                    <DeleteIcon />
                                  </IconButton>
                                )}
                                {!user?.is_admin && (
                                  <Typography variant="caption" color="text.secondary">
                                    -
                                  </Typography>
                                )}
                              </Box>
                            </TableCell>
                          </TableRow>
                        );
                      })
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Create User Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User / Sub-Admin</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                label="Username *"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Email *"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Password *"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                fullWidth
                required
                InputProps={{
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
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Phone Number"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={formData.role}
                  label="Role"
                  onChange={(e) => {
                    const role = e.target.value;
                    setFormData({ 
                      ...formData, 
                      role: role,
                      specialization: role !== 'doctor' ? '' : formData.specialization,
                      is_sub_admin: false
                    });
                  }}
                >
                  <MenuItem value="">None</MenuItem>
                  <MenuItem value="doctor">Doctor</MenuItem>
                  <MenuItem value="nurse">Nurse</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {formData.role === 'doctor' && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Specialization</InputLabel>
                  <Select
                    value={formData.specialization}
                    label="Specialization"
                    onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                  >
                    <MenuItem value="Cardiologist">Cardiologist</MenuItem>
                    <MenuItem value="Psychiatrist">Psychiatrist</MenuItem>
                    <MenuItem value="Psychologist">Psychologist</MenuItem>
                    <MenuItem value="Neurologist">Neurologist</MenuItem>
                    <MenuItem value="General Practitioner">General Practitioner</MenuItem>
                    <MenuItem value="Family Medicine">Family Medicine</MenuItem>
                    <MenuItem value="Internal Medicine">Internal Medicine</MenuItem>
                    <MenuItem value="Pediatrician">Pediatrician</MenuItem>
                    <MenuItem value="Other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', mt: 1, mb: 1 }}>
                Note: Profile image and description can be updated by the user after account creation.
              </Typography>
              <Divider sx={{ my: 2 }} />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_sub_admin}
                    onChange={(e) => setFormData({ ...formData, is_sub_admin: e.target.checked })}
                  />
                }
                label="Create as Sub-Admin"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_admin}
                    onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
                  />
                }
                label="Create as Full Administrator (requires main admin privileges)"
                disabled={!user?.is_admin}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleCreateUser}
            variant="contained"
            sx={{
              bgcolor: colors.darkGreen,
              '&:hover': { bgcolor: '#134030' },
            }}
            disabled={loading}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog 
        open={openEditDialog} 
        onClose={() => {
          setOpenEditDialog(false);
          setEditingUser(null);
          setEditFormData({
            username: '',
            email: '',
            phone_number: '',
            is_admin: false,
            is_sub_admin: false,
            role: '',
            specialization: '',
          });
        }} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>Edit User Profile</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                label="Username *"
                value={editFormData.username}
                onChange={(e) => setEditFormData({ ...editFormData, username: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Email *"
                type="email"
                value={editFormData.email}
                onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Phone Number"
                value={editFormData.phone_number}
                onChange={(e) => setEditFormData({ ...editFormData, phone_number: e.target.value })}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={editFormData.role}
                  label="Role"
                  onChange={(e) => {
                    const role = e.target.value;
                    setEditFormData({ 
                      ...editFormData, 
                      role: role,
                      specialization: role !== 'doctor' ? '' : editFormData.specialization,
                    });
                  }}
                >
                  <MenuItem value="">None</MenuItem>
                  <MenuItem value="doctor">Doctor</MenuItem>
                  <MenuItem value="nurse">Nurse</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {editFormData.role === 'doctor' && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Specialization</InputLabel>
                  <Select
                    value={editFormData.specialization}
                    label="Specialization"
                    onChange={(e) => setEditFormData({ ...editFormData, specialization: e.target.value })}
                  >
                    <MenuItem value="Cardiologist">Cardiologist</MenuItem>
                    <MenuItem value="Psychiatrist">Psychiatrist</MenuItem>
                    <MenuItem value="Psychologist">Psychologist</MenuItem>
                    <MenuItem value="Neurologist">Neurologist</MenuItem>
                    <MenuItem value="General Practitioner">General Practitioner</MenuItem>
                    <MenuItem value="Family Medicine">Family Medicine</MenuItem>
                    <MenuItem value="Internal Medicine">Internal Medicine</MenuItem>
                    <MenuItem value="Pediatrician">Pediatrician</MenuItem>
                    <MenuItem value="Other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editFormData.is_sub_admin}
                    onChange={(e) => setEditFormData({ ...editFormData, is_sub_admin: e.target.checked })}
                  />
                }
                label="Sub-Admin"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editFormData.is_admin}
                    onChange={(e) => setEditFormData({ ...editFormData, is_admin: e.target.checked })}
                  />
                }
                label="Full Administrator"
                disabled={!user?.is_admin}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              setOpenEditDialog(false);
              setEditingUser(null);
              setEditFormData({
                username: '',
                email: '',
                phone_number: '',
                is_admin: false,
                is_sub_admin: false,
                role: '',
                specialization: '',
              });
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpdateUser}
            variant="contained"
            sx={{
              bgcolor: colors.darkGreen,
              '&:hover': { bgcolor: '#134030' },
            }}
            disabled={loading}
          >
            {loading ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default UserManagement;

