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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  LocalHospital as LocalHospitalIcon,
  MedicalServices as MedicalServicesIcon,
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
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [nurses, setNurses] = useState([]);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [selectedNurse, setSelectedNurse] = useState('');
  const [assignmentType, setAssignmentType] = useState('doctor'); // 'doctor' or 'nurse'
  const [assignmentNotes, setAssignmentNotes] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    loadConnectData();
    checkUserRole();
  }, []);

  const checkUserRole = async () => {
    try {
      const response = await api.get('/auth/me');
      const user = response.data;
      const isAdmin = user.is_admin || user.is_sub_admin;
      const isNurse = user.role === 'nurse';
      const isDoctor = user.role === 'doctor';
      setUserRole({ isAdmin, isNurse, isDoctor, canAssign: isAdmin || isNurse || isDoctor });
    } catch (error) {
      console.error('Failed to check user role:', error);
    }
  };

  const loadConnectData = async () => {
    try {
      // Load patients and doctors/nurses if user is admin, nurse, or doctor
      if (userRole?.canAssign) {
        try {
          const patientsResponse = await api.get('/admin/patients');
          setPatients(patientsResponse.data.patients || []);

          const doctorsResponse = await api.get('/admin/doctors');
          setDoctors(doctorsResponse.data.doctors || []);

          // Load nurses
          const nursesResponse = await api.get('/admin/nurses');
          setNurses(nursesResponse.data.nurses || []);
        } catch (error) {
          console.error('Failed to load patients/doctors/nurses:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load connect data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userRole?.canAssign) {
      loadConnectData();
    }
  }, [userRole]);

  const handleAssignDoctor = (patient) => {
    setSelectedPatient(patient);
    setSelectedDoctor(patient.assigned_doctor?.id || '');
    setSelectedNurse(patient.assigned_nurse?.id || '');
    setAssignmentType(patient.assigned_doctor ? 'doctor' : patient.assigned_nurse ? 'nurse' : 'doctor');
    setAssignmentNotes('');
    setAssignDialogOpen(true);
  };

  const handleSubmitAssignment = async () => {
    if (!selectedPatient) {
      setSnackbar({
        open: true,
        message: 'Please select a patient',
        severity: 'error',
      });
      return;
    }

    if (assignmentType === 'doctor' && !selectedDoctor) {
      setSnackbar({
        open: true,
        message: 'Please select a doctor',
        severity: 'error',
      });
      return;
    }

    if (assignmentType === 'nurse' && !selectedNurse) {
      setSnackbar({
        open: true,
        message: 'Please select a nurse',
        severity: 'error',
      });
      return;
    }

    try {
      const payload = {
        patient_id: selectedPatient.id,
        notes: assignmentNotes,
      };

      if (assignmentType === 'doctor') {
        payload.doctor_id = selectedDoctor;
      } else {
        payload.nurse_id = selectedNurse;
      }

      await api.post('/admin/assign-doctor', payload);

      const roleName = assignmentType === 'doctor' ? 'Doctor' : 'Nurse';
      setSnackbar({
        open: true,
        message: `${roleName} assigned successfully! Notification sent.`,
        severity: 'success',
      });

      setAssignDialogOpen(false);
      setSelectedPatient(null);
      setSelectedDoctor('');
      setSelectedNurse('');
      setAssignmentType('doctor');
      setAssignmentNotes('');

      // Reload data
      loadConnectData();
    } catch (error) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || `Failed to assign ${assignmentType}`,
        severity: 'error',
      });
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
        {/* Patients Section - Only for Admin/Nurse */}
        {userRole?.canAssign && (
          <Grid item xs={12}>
            <Card sx={{ borderRadius: 3, boxShadow: 2, mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    Patients
                  </Typography>
                </Box>
                {patients.length === 0 ? (
                  <Typography color="text.secondary">No patients found</Typography>
                ) : (
                  <TableContainer component={Paper} sx={{ mt: 2 }}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Patient Name</TableCell>
                          <TableCell>Email</TableCell>
                          <TableCell>Assigned Doctor/Nurse</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {patients.map((patient) => (
                          <TableRow key={patient.id}>
                            <TableCell>{patient.username || 'Unknown'}</TableCell>
                            <TableCell>{patient.email || 'N/A'}</TableCell>
                            <TableCell>
                              {patient.assigned_doctor ? (
                                <Chip
                                  label={`Dr. ${patient.assigned_doctor.username}`}
                                  color="primary"
                                  size="small"
                                  icon={<LocalHospitalIcon />}
                                />
                              ) : patient.assigned_nurse ? (
                                <Chip
                                  label={`Nurse ${patient.assigned_nurse.username}`}
                                  color="secondary"
                                  size="small"
                                  icon={<MedicalServicesIcon />}
                                />
                              ) : (
                                <Chip label="Not Assigned" color="default" size="small" />
                              )}
                            </TableCell>
                            <TableCell>
                              <Button
                                variant="outlined"
                                size="small"
                                startIcon={<PersonAddIcon />}
                                onClick={() => handleAssignDoctor(patient)}
                                sx={{ color: colors.darkGreen, borderColor: colors.darkGreen }}
                              >
                                {patient.assigned_doctor || patient.assigned_nurse ? 'Reassign' : 'Assign'}
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Available Doctors and Nurses Section */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 3, boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Available Doctors and Nurses
              </Typography>
              {doctors.length === 0 && nurses.length === 0 ? (
                <Typography color="text.secondary" sx={{ mt: 2 }}>
                  No doctors or nurses available
                </Typography>
              ) : (
                <Box sx={{ mt: 2 }}>
                  {/* Doctors Section */}
                  {doctors.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: colors.darkGreen }}>
                        Doctors ({doctors.length})
                      </Typography>
                      <Grid container spacing={2}>
                        {doctors.map((doctor) => (
                          <Grid item xs={12} md={6} lg={4} key={doctor.id}>
                            <Card
                              sx={{
                                p: 2,
                                bgcolor: colors.veryLightBlue,
                                borderRadius: 2,
                                borderLeft: `4px solid ${colors.darkGreen}`,
                              }}
                            >
                              <Box sx={{ display: 'flex', alignItems: 'start', gap: 2 }}>
                                <Box
                                  sx={{
                                    bgcolor: colors.darkGreen,
                                    borderRadius: '50%',
                                    width: 48,
                                    height: 48,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: 'white',
                                  }}
                                >
                                  <LocalHospitalIcon />
                                </Box>
                                <Box sx={{ flex: 1 }}>
                                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                    {doctor.username || 'Unknown'}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    {doctor.email || 'N/A'}
                                  </Typography>
                                  {doctor.specialization && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                      Specialization: {doctor.specialization}
                                    </Typography>
                                  )}
                                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                    Assigned Patients: {doctor.assigned_patients_count || 0}
                                  </Typography>
                                  <Chip
                                    label="Doctor"
                                    size="small"
                                    sx={{
                                      mt: 1,
                                      bgcolor: colors.darkGreen,
                                      color: 'white',
                                    }}
                                  />
                                </Box>
                              </Box>
                            </Card>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  )}

                  {/* Nurses Section */}
                  {nurses.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: colors.darkGreen }}>
                        Nurses ({nurses.length})
                      </Typography>
                      <Grid container spacing={2}>
                        {nurses.map((nurse) => (
                          <Grid item xs={12} md={6} lg={4} key={nurse.id}>
                            <Card
                              sx={{
                                p: 2,
                                bgcolor: colors.creamYellow,
                                borderRadius: 2,
                                borderLeft: `4px solid ${colors.darkGreen}`,
                              }}
                            >
                              <Box sx={{ display: 'flex', alignItems: 'start', gap: 2 }}>
                                <Box
                                  sx={{
                                    bgcolor: colors.darkGreen,
                                    borderRadius: '50%',
                                    width: 48,
                                    height: 48,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: 'white',
                                  }}
                                >
                                  <MedicalServicesIcon />
                                </Box>
                                <Box sx={{ flex: 1 }}>
                                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                    {nurse.username || 'Unknown'}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    {nurse.email || 'N/A'}
                                  </Typography>
                                  {nurse.phone_number && (
                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                      Phone: {nurse.phone_number}
                                    </Typography>
                                  )}
                                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                    Assigned Patients: {nurse.assigned_patients_count || 0}
                                  </Typography>
                                  <Chip
                                    label="Nurse"
                                    size="small"
                                    sx={{
                                      mt: 1,
                                      bgcolor: colors.darkGreen,
                                      color: 'white',
                                    }}
                                  />
                                </Box>
                              </Box>
                            </Card>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Assign Doctor/Nurse Dialog */}
      <Dialog open={assignDialogOpen} onClose={() => setAssignDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Assign Doctor or Nurse to Patient</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              <strong>Patient:</strong> {selectedPatient?.username || 'Unknown'}
            </Typography>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Assignment Type</InputLabel>
              <Select
                value={assignmentType}
                onChange={(e) => {
                  setAssignmentType(e.target.value);
                  setSelectedDoctor('');
                  setSelectedNurse('');
                }}
                label="Assignment Type"
              >
                <MenuItem value="doctor">Doctor</MenuItem>
                <MenuItem value="nurse">Nurse</MenuItem>
              </Select>
            </FormControl>

            {assignmentType === 'doctor' ? (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Doctor</InputLabel>
                <Select
                  value={selectedDoctor}
                  onChange={(e) => setSelectedDoctor(e.target.value)}
                  label="Select Doctor"
                >
                  {doctors.map((doctor) => (
                    <MenuItem key={doctor.id} value={doctor.id}>
                      {doctor.username} {doctor.email ? `(${doctor.email})` : ''}
                      {doctor.assigned_patients_count > 0 && ` - ${doctor.assigned_patients_count} patients`}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Nurse</InputLabel>
                <Select
                  value={selectedNurse}
                  onChange={(e) => setSelectedNurse(e.target.value)}
                  label="Select Nurse"
                >
                  {nurses.map((nurse) => (
                    <MenuItem key={nurse.id} value={nurse.id}>
                      {nurse.username} {nurse.email ? `(${nurse.email})` : ''}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Notes (Optional)"
              value={assignmentNotes}
              onChange={(e) => setAssignmentNotes(e.target.value)}
              placeholder="Add any notes about this assignment..."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSubmitAssignment}
            variant="contained"
            sx={{ bgcolor: colors.darkGreen, '&:hover': { bgcolor: '#0f3d2f' } }}
          >
            Assign {assignmentType === 'doctor' ? 'Doctor' : 'Nurse'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default Connect;

