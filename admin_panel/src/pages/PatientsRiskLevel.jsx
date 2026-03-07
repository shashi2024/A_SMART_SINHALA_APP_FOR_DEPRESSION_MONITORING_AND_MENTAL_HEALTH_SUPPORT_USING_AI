import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  CalendarToday,
  People,
  Description,
  Videocam,
  Visibility,
  FiberManualRecord,
  Assessment,
  Security,
  Close,
} from '@mui/icons-material';

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
  purple: '#9C27B0',
  red: '#F44336',
  orange: '#FF9800',
  blue: '#2196F3',
};

function PatientsRiskLevel() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [diagModalOpen, setDiagModalOpen] = useState(false);
  const [fakeModalOpen, setFakeModalOpen] = useState(false);
  const [diagData, setDiagData] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDiagnostics = async (user) => {
    setSelectedUser(user);
    setModalLoading(true);
    try {
      const response = await api.get(`/admin/user/${user.user_id}/diagnostics`);
      setDiagData(response.data);
    } catch (error) {
      console.error('Failed to fetch diagnostics:', error);
    } finally {
      setModalLoading(false);
    }
  };

  const handleRiskClick = (e, user) => {
    e.stopPropagation();
    fetchDiagnostics(user);
    setDiagModalOpen(true);
  };

  const handleFakeClick = (e, user) => {
    e.stopPropagation();
    fetchDiagnostics(user);
    setFakeModalOpen(true);
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'severe':
      case 'high':
        return colors.red;
      case 'moderate':
        return colors.orange;
      default:
        return colors.darkGreen;
    }
  };

  const getRiskLabel = (riskLevel) => {
    switch (riskLevel) {
      case 'severe':
      case 'high':
        return 'High';
      case 'moderate':
        return 'Mid';
      default:
        return 'Low';
    }
  };

  const getFakeStatusChip = (score) => {
    const percentage = (score * 100).toFixed(1);
    const isHighRisk = score >= 0.6;

    return (
      <Chip
        label={`${percentage}%`}
        size="small"
        sx={{
          bgcolor: isHighRisk ? colors.red : colors.darkGreen,
          color: 'white',
          fontWeight: 600,
          borderRadius: 2,
          minWidth: '60px',
          cursor: 'pointer',
          '&:hover': { opacity: 0.8 }
        }}
        title={isHighRisk ? "High likelihood of fake user - Click for details" : "Likely authentic user - Click for details"}
      />
    );
  };

  // Calculate statistics
  const totalUsers = users.length;
  const highRiskUsers = users.filter((u) => u.risk_level === 'high' || u.risk_level === 'severe').length;
  const midRiskUsers = users.filter((u) => u.risk_level === 'moderate').length;
  const lowRiskUsers = users.filter((u) => u.risk_level === 'low' || !u.risk_level).length;

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', padding: 20 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 4 }}>
        Patients Risk Level
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.purple,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {totalUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Total Users
                  </Typography>
                </Box>
                <CalendarToday sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.red,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {highRiskUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    High Risk Users
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.orange,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {midRiskUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Mid Risk Users
                  </Typography>
                </Box>
                <Description sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              bgcolor: colors.blue,
              color: 'white',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {lowRiskUsers.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Low Risk Users
                  </Typography>
                </Box>
                <Videocam sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Patients Table */}
      <TableContainer
        component={Paper}
        sx={{
          borderRadius: 3,
          boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
        }}
      >
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F5F5F5' }}>
              <TableCell sx={{ fontWeight: 'bold' }}>Username</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Email</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Total Sessions</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Current Risk</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>PHQ-9 Result</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Fake User Risk</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Last Activity</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    No users found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow
                  key={user.user_id}
                  hover
                  onClick={() => navigate(`/users/${user.user_id}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{user.username || 'N/A'}</TableCell>
                  <TableCell>{user.email || 'N/A'}</TableCell>
                  <TableCell>{user.total_sessions ?? 0}</TableCell>
                  <TableCell>
                    <Chip
                      label={getRiskLabel(user.risk_level)}
                      size="small"
                      onClick={(e) => handleRiskClick(e, user)}
                      sx={{
                        bgcolor: getRiskColor(user.risk_level),
                        color: 'white',
                        fontWeight: 600,
                        borderRadius: 2,
                        cursor: 'pointer',
                        '&:hover': { opacity: 0.8 }
                      }}
                    />
                  </TableCell>
                  <TableCell onClick={(e) => handleRiskClick(e, user)}>
                    {user.phq9_score !== undefined && user.phq9_score !== null ? (
                      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          Score: {user.phq9_score}/27
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#666' }}>
                          {user.phq9_severity || 'N/A'}
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2" sx={{ color: '#9e9e9e' }}>Pending</Typography>
                    )}
                  </TableCell>
                  <TableCell onClick={(e) => handleFakeClick(e, user)}>
                    {getFakeStatusChip(user.fake_score || 0)}
                  </TableCell>
                  <TableCell>
                    {user.last_activity
                      ? new Date(user.last_activity).toLocaleString()
                      : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {(() => {
                      const lastSeen = user.last_activity ? new Date(user.last_activity) : null;
                      const isOnline = lastSeen && (new Date() - lastSeen) < (5 * 60 * 1000);
                      return (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <FiberManualRecord sx={{ fontSize: 12, color: isOnline ? '#4caf50' : '#9e9e9e' }} />
                          <Typography variant="body2" sx={{ color: isOnline ? '#4caf50' : '#9e9e9e', fontWeight: 600 }}>
                            {isOnline ? 'Online' : 'Offline'}
                          </Typography>
                        </Box>
                      );
                    })()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/users/${user.user_id}`);
                      }}
                      sx={{ color: colors.darkGreen }}
                    >
                      <Visibility fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Risk Diagnostics Modal */}
      <Dialog
        open={diagModalOpen}
        onClose={() => setDiagModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, padding: 1 }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment sx={{ color: colors.darkGreen }} />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Risk Assessment Details - {selectedUser?.username}
            </Typography>
          </Box>
          <IconButton onClick={() => setDiagModalOpen(false)} size="small">
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {modalLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={30} />
            </Box>
          ) : diagData ? (
            <Grid container spacing={3}>
              {/* PHQ-9 Section */}
              <Grid item xs={12}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: colors.darkGreen, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  PHQ-9 Mental Health Questionnaire
                  {diagData.phq9 && (
                    <Chip
                      label={`Score: ${diagData.phq9.score}/27`}
                      size="small"
                      color="primary"
                      sx={{ ml: 1, fontWeight: 'bold' }}
                    />
                  )}
                </Typography>
                {diagData.phq9 ? (
                  <Box>
                    <Typography variant="body2" sx={{ mb: 2, fontStyle: 'italic', color: '#666' }}>
                      Completed on: {new Date(diagData.phq9.completed_at).toLocaleString()} | Severity: {diagData.phq9.severity}
                    </Typography>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 'bold' }}>#</TableCell>
                          <TableCell sx={{ fontWeight: 'bold' }}>Question</TableCell>
                          <TableCell sx={{ fontWeight: 'bold' }}>Response</TableCell>
                          <TableCell sx={{ fontWeight: 'bold' }}>Score</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {diagData.phq9.qa && Array.isArray(diagData.phq9.qa) ? (
                          diagData.phq9.qa.map((item) => (
                            <TableRow key={item.question_num}>
                              <TableCell>{item.question_num}</TableCell>
                              <TableCell>{item.question}</TableCell>
                              <TableCell sx={{ fontWeight: 500 }}>{item.answer}</TableCell>
                              <TableCell align="center">{item.score}</TableCell>
                            </TableRow>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={4} align="center">No questionnaire details available</TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </Box>
                ) : (
                  <Typography variant="body2" sx={{ color: '#666', py: 2 }}>No PHQ-9 data available for this user.</Typography>
                )}
              </Grid>

              <Grid item xs={12}><Divider /></Grid>

              {/* Keystroke Section */}
              <Grid item xs={12}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: colors.darkGreen, mb: 2 }}>
                  Keystroke Stress Diagnostics
                </Typography>
                {diagData.typing ? (
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Card variant="outlined" sx={{ textAlign: 'center', p: 2, borderRadius: 2, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <Typography variant="caption" sx={{ color: '#666', textTransform: 'uppercase' }}>Current Risk</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold', color: getRiskColor(diagData.typing?.risk_level) }}>
                          {diagData.typing?.risk_level?.toUpperCase() || 'UNSET'}
                        </Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Card variant="outlined" sx={{ textAlign: 'center', p: 2, borderRadius: 2, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <Typography variant="caption" sx={{ color: '#666', textTransform: 'uppercase' }}>Depression Score</Typography>
                        <Typography variant="h5" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                          {diagData.typing?.depression_score !== undefined
                            ? `${(diagData.typing.depression_score * 100).toFixed(1)}%`
                            : 'N/A'}
                        </Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={12}>
                      <Box sx={{ bgcolor: '#f9f9f9', p: 2, borderRadius: 2 }}>
                        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>Metrics Summary</Typography>
                        <Grid container spacing={1}>
                          {diagData.typing.metrics && Object.entries(diagData.typing.metrics).map(([key, value]) => (
                            <Grid item xs={6} key={key}>
                              <Typography variant="caption" sx={{ display: 'block', color: '#666' }}>{key.replace(/_/g, ' ')}</Typography>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>{typeof value === 'number' ? value.toFixed(4) : value}</Typography>
                            </Grid>
                          ))}
                        </Grid>
                      </Box>
                    </Grid>
                  </Grid>
                ) : (
                  <Typography variant="body2" sx={{ color: '#666' }}>No keystroke diagnostic data available.</Typography>
                )}
              </Grid>
            </Grid>
          ) : (
            <Typography>Failed to load data.</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDiagModalOpen(false)} color="primary">Close</Button>
        </DialogActions>
      </Dialog>

      {/* Fake User Indicators Modal */}
      <Dialog
        open={fakeModalOpen}
        onClose={() => setFakeModalOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, padding: 1 }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Security sx={{ color: colors.red }} />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Fake User Detection Details
            </Typography>
          </Box>
          <IconButton onClick={() => setFakeModalOpen(false)} size="small">
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {modalLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={30} />
            </Box>
          ) : diagData ? (
            <List sx={{ pt: 0 }}>
              <ListItem sx={{ px: 0, flexDirection: 'column', alignItems: 'flex-start' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>Typing Patterns</Typography>
                <Box sx={{ width: '100%', bgcolor: diagData.fake_indicators.typing?.overall_assessment?.is_fake ? '#fff1f0' : '#f6ffed', p: 2, borderRadius: 2, border: '1px solid', borderColor: diagData.fake_indicators.typing?.overall_assessment?.is_fake ? '#ffa39e' : '#b7eb8f' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Likelihood of Fake:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{((diagData.fake_indicators?.typing?.overall_assessment?.avg_fake_score || 0) * 100).toFixed(1)}%</Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="caption" sx={{ color: '#666' }}>
                    Analyzed across {diagData.fake_indicators?.typing?.total_samples || 0} samples.
                    Main indicator: {diagData.fake_indicators?.typing?.overall_assessment?.is_fake ? "Highly repetitive and machine-like timing detected." : "Natural variation in keystroke timing observed."}
                  </Typography>
                </Box>
              </ListItem>

              <ListItem sx={{ px: 0, mt: 2, flexDirection: 'column', alignItems: 'flex-start' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>Voice/Speech Patterns</Typography>
                <Box sx={{ width: '100%', bgcolor: diagData.fake_indicators.voice?.overall_assessment?.is_fake ? '#fff1f0' : '#f6ffed', p: 2, borderRadius: 2, border: '1px solid', borderColor: diagData.fake_indicators.voice?.overall_assessment?.is_fake ? '#ffa39e' : '#b7eb8f' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Likelihood of Fake:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{((diagData.fake_indicators?.voice?.overall_assessment?.avg_fake_score || 0) * 100).toFixed(1)}%</Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="caption" sx={{ color: '#666' }}>
                    Detected via {diagData.fake_indicators?.voice?.total_samples || 0} voice recordings.
                    Status: {diagData.fake_indicators?.voice?.overall_assessment?.is_fake ? "Synthetic or recorded voice signatures detected." : "Organic voice characteristics confirmed."}
                  </Typography>
                </Box>
              </ListItem>
            </List>
          ) : (
            <Typography>Failed to load data.</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFakeModalOpen(false)} sx={{ color: colors.darkGreen }}>Done</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default PatientsRiskLevel;



















































