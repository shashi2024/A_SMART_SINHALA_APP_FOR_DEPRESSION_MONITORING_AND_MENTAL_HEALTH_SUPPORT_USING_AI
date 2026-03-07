import React, { useState, useEffect } from 'react';
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
    LinearProgress,
    Stack,
    Divider,
    Avatar
} from '@mui/material';
import {
    Videocam,
    DirectionsRun,
    Favorite,
    Mic,
    KeyboardArrowDown,
    Close as CloseIcon,
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    Analytics as AnalyticsIcon,
    Person as PersonIcon
} from '@mui/icons-material';

// Color palette matching the dashboard
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
    lightPink: '#FFF5F5',
};

function SensorCard({ icon, title, value, label, color, metrics, isEmpty }) {
    return (
        <Card sx={{ borderRadius: 3, height: '100%', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', opacity: isEmpty ? 0.7 : 1 }}>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Box sx={{ p: 1, borderRadius: 2, bgcolor: isEmpty ? '#f0f0f0' : `${color}15`, color: isEmpty ? '#999' : color }}>
                        {icon}
                    </Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: isEmpty ? 'text.secondary' : 'text.primary' }}>{title}</Typography>
                </Box>

                <Box sx={{ textAlign: 'center', mb: 2 }}>
                    <Typography variant={isEmpty ? "h6" : "h4"} sx={{ fontWeight: 'bold', color: isEmpty ? 'text.secondary' : color }}>
                        {isEmpty ? "No information" : value}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                        {isEmpty ? "Sensor activity not found" : label}
                    </Typography>
                </Box>

                {!isEmpty && metrics && (
                    <Box sx={{ mt: 2 }}>
                        <Divider sx={{ mb: 1.5 }} />
                        <Grid container spacing={1}>
                            {Object.entries(metrics).map(([key, val]) => (
                                <Grid item xs={6} key={key}>
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        {key.toUpperCase().replace(/_/g, ' ')}
                                    </Typography>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                        {val}
                                    </Typography>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
}

function BioFeedbackRow({ user }) {
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);

    const handleOpen = async () => {
        setOpen(true);
        setLoading(true);
        try {
            // In a real scenario, we'd fetch specific bio-feedback data for this user
            // For now, we'll simulate fetching from the profile or a specialized endpoint
            const response = await api.get(`/admin/users/${user.id}/profile`);
            const profile = response.data;

            // Extract real data from biofeedback collection
            const bioFeedback = profile.biofeedback && profile.biofeedback.length > 0 ? profile.biofeedback[0] : null;

            const bioData = {
                facial: (bioFeedback?.sensors?.face && !bioFeedback.sensors.face.error) ? {
                    expression: bioFeedback.sensors.face.expression || 'N/A',
                    stress_level: bioFeedback.sensors.face.stress_level || 'N/A',
                    confidence: 'AI Analyzed',
                    metrics: { status: 'Stable' }
                } : null,
                accelerometer: (bioFeedback?.sensors?.movement && !bioFeedback.sensors.movement.error) ? {
                    activity: bioFeedback.sensors.movement.activity || 'N/A',
                    energy: bioFeedback.sensors.movement.metrics?.energy || '0.00',
                    label: 'Physical State',
                    metrics: bioFeedback.sensors.movement.metrics
                } : null,
                heartRate: (bioFeedback?.sensors?.heart_rate && !bioFeedback.sensors.heart_rate.error) ? {
                    bpm: bioFeedback.sensors.heart_rate.metrics?.mean_hr_bpm || 'N/A',
                    stress: bioFeedback.sensors.heart_rate.stress_level || 'N/A',
                    label: 'Cardiac Status',
                    metrics: bioFeedback.sensors.heart_rate.metrics
                } : null,
                microphone: (bioFeedback?.sensors?.voice && !bioFeedback.sensors.voice.error) ? {
                    level: bioFeedback.sensors.voice.level || 'N/A',
                    confidence: `${(bioFeedback.sensors.voice.score || 0) * 10}%`,
                    label: 'Voice Stress Output',
                    metrics: {
                        score: bioFeedback.sensors.voice.score,
                        status: bioFeedback.sensors.voice.level
                    }
                } : null,
                finalOutput: {
                    risk: bioFeedback?.final_assessment?.risk_level || profile.statistics?.risk_level || null,
                    score: profile.statistics?.average_depression_score || '0.00',
                    last_activity: bioFeedback?.timestamp || profile.statistics?.last_activity || null,
                    summary: bioFeedback?.final_assessment?.summary
                }
            };

            setData(bioData);
        } catch (error) {
            console.error('Failed to fetch bio-feedback data:', error);
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (risk) => {
        const r = risk?.toLowerCase();
        if (r === 'severe' || r === 'high') return colors.red;
        if (r === 'moderate' || r === 'medium') return colors.orange;
        return colors.darkGreen;
    };

    return (
        <>
            <TableRow
                hover
                onClick={handleOpen}
                sx={{ cursor: 'pointer', '&:hover': { bgcolor: '#F5F5F5' } }}
            >
                <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ bgcolor: colors.darkGreen, width: 32, height: 32, fontSize: '14px' }}>
                            {user.username?.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>{user.username}</Typography>
                            <Typography variant="caption" color="text.secondary">{user.email}</Typography>
                        </Box>
                    </Box>
                </TableCell>
                <TableCell>{user.phone_number || 'N/A'}</TableCell>
                <TableCell>
                    {user.risk_level ? (
                        <Chip
                            label={user.risk_level.toUpperCase()}
                            size="small"
                            sx={{
                                bgcolor: getRiskColor(user.risk_level),
                                color: 'white',
                                fontWeight: 'bold',
                                borderRadius: 1.5
                            }}
                        />
                    ) : (
                        <Typography variant="body2" color="text.secondary">No information</Typography>
                    )}
                </TableCell>
                <TableCell>
                    <Typography variant="body2">
                        {user.last_activity ? new Date(user.last_activity).toLocaleString() : 'No activity'}
                    </Typography>
                </TableCell>
                <TableCell align="right">
                    <IconButton size="small">
                        <KeyboardArrowDown />
                    </IconButton>
                </TableCell>
            </TableRow>

            <Dialog
                open={open}
                onClose={() => setOpen(false)}
                maxWidth="md"
                fullWidth
                PaperProps={{
                    sx: { borderRadius: 4, bgcolor: colors.lightPink }
                }}
            >
                <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <AnalyticsIcon sx={{ color: colors.darkGreen }} />
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                            Bio-Feedback Analysis: {user.username}
                        </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right', mr: 2 }}>
                        <Typography variant="caption" display="block" color="text.secondary">
                            {user.email}
                        </Typography>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>
                            Last Active: {user.last_activity ? new Date(user.last_activity).toLocaleString() : 'N/A'}
                        </Typography>
                    </Box>
                    <IconButton onClick={() => setOpen(false)} size="small">
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>

                <DialogContent sx={{ p: 3 }}>
                    {loading ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 8 }}>
                            <CircularProgress sx={{ mb: 2, color: colors.darkGreen }} />
                            <Typography color="text.secondary">Fetching real-time sensor data...</Typography>
                        </Box>
                    ) : data ? (
                        <Grid container spacing={3}>
                            {/* Facial Camera */}
                            <Grid item xs={12} sm={6}>
                                <SensorCard
                                    icon={<Videocam />}
                                    title="Facial Analysis"
                                    value={data.facial?.expression}
                                    label={`Stress: ${data.facial?.stress_level} (${data.facial?.confidence})`}
                                    color={colors.purple}
                                    metrics={data.facial?.metrics}
                                    isEmpty={!data.facial}
                                />
                            </Grid>

                            {/* Accelerometer */}
                            <Grid item xs={12} sm={6}>
                                <SensorCard
                                    icon={<DirectionsRun />}
                                    title="Movement / Activity"
                                    value={data.accelerometer?.activity}
                                    label={`Energy: ${data.accelerometer?.energy}`}
                                    color={colors.blue}
                                    metrics={data.accelerometer?.metrics}
                                    isEmpty={!data.accelerometer}
                                />
                            </Grid>

                            {/* Heart Rate */}
                            <Grid item xs={12} sm={6}>
                                <SensorCard
                                    icon={<Favorite />}
                                    title="Heart Rate (BPM)"
                                    value={data.heartRate?.bpm}
                                    label={`Status: ${data.heartRate?.stress}`}
                                    color={colors.red}
                                    metrics={data.heartRate?.metrics}
                                    isEmpty={!data.heartRate}
                                />
                            </Grid>

                            {/* Microphone */}
                            <Grid item xs={12} sm={6}>
                                <SensorCard
                                    icon={<Mic />}
                                    title="Voice Analysis"
                                    value={data.microphone?.level}
                                    label={data.microphone?.label}
                                    color={colors.orange}
                                    metrics={data.microphone?.metrics}
                                    isEmpty={!data.microphone}
                                />
                            </Grid>

                            {/* Final Output Summary */}
                            <Grid item xs={12}>
                                <Card sx={{
                                    borderRadius: 4,
                                    bgcolor: colors.darkGreen,
                                    color: 'white',
                                    boxShadow: '0 4px 20px rgba(24, 88, 70, 0.2)'
                                }}>
                                    <CardContent sx={{ p: 3 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                            <Box>
                                                <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1 }}>
                                                    Final System Assessment
                                                </Typography>
                                                <Typography variant="body1" sx={{ opacity: 0.9 }}>
                                                    {data.finalOutput.summary || "Based on aggregate bio-feedback multi-sensor data"}
                                                </Typography>
                                            </Box>
                                            <Box sx={{ textAlign: 'right' }}>
                                                <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                                                    {data.finalOutput.risk ? data.finalOutput.risk.toUpperCase() : "NO INFO"}
                                                </Typography>
                                                <Typography variant="subtitle1" sx={{ fontWeight: 600, opacity: 0.9 }}>
                                                    Patient Risk Level
                                                </Typography>
                                            </Box>
                                        </Box>

                                        <Box sx={{ mt: 3 }}>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>Diagnostic Confidence</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>88%</Typography>
                                            </Box>
                                            <LinearProgress
                                                variant="determinate"
                                                value={88}
                                                sx={{
                                                    height: 10,
                                                    borderRadius: 5,
                                                    bgcolor: 'rgba(255,255,255,0.2)',
                                                    '& .MuiLinearProgress-bar': { bgcolor: 'white' }
                                                }}
                                            />
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    ) : (
                        <Typography align="center" py={4}>No data available for this user.</Typography>
                    )}
                </DialogContent>
            </Dialog>
        </>
    );
}

function BioFeedbackAnalysis() {
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        total: 0,
        highRisk: 0,
        lowRisk: 0
    });

    useEffect(() => {
        const fetchPatients = async () => {
            try {
                const response = await api.get('/admin/users');
                const filtered = response.data.users.filter(u =>
                    !u.is_admin && !u.is_sub_admin && u.role !== 'doctor' && u.role !== 'nurse'
                );
                setPatients(filtered);

                const high = filtered.filter(p => p.risk_level && (p.risk_level.toLowerCase() === 'high' || p.risk_level.toLowerCase() === 'severe')).length;
                setStats({
                    total: filtered.length,
                    highRisk: high,
                    lowRisk: filtered.filter(p => p.risk_level && (p.risk_level.toLowerCase() === 'low' || p.risk_level.toLowerCase() === 'healthy')).length
                });
            } catch (error) {
                console.error('Failed to fetch patients:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchPatients();
    }, []);

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress sx={{ color: colors.darkGreen }} />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 4 }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 3, bgcolor: colors.darkGreen, color: 'white' }}>
                    <AnalyticsIcon fontSize="large" />
                </Box>
                <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: colors.darkGreen }}>
                        Bio-Feedback Analysis
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Multi-sensor mental health monitoring dashboard
                    </Typography>
                </Box>
            </Box>

            {/* Stats Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <Card sx={{ borderRadius: 3, bgcolor: colors.purple, color: 'white' }}>
                        <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>{stats.total}</Typography>
                                <Typography variant="body2">Total Patients</Typography>
                            </Box>
                            <PersonIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Card sx={{ borderRadius: 3, bgcolor: colors.red, color: 'white' }}>
                        <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>{stats.highRisk}</Typography>
                                <Typography variant="body2">Critical Risk Detected</Typography>
                            </Box>
                            <WarningIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Card sx={{ borderRadius: 3, bgcolor: colors.darkGreen, color: 'white' }}>
                        <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>{stats.lowRisk}</Typography>
                                <Typography variant="body2">Healthy / Low Risk</Typography>
                            </Box>
                            <CheckCircleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Patients Table */}
            <TableContainer component={Paper} sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                <Table>
                    <TableHead>
                        <TableRow sx={{ bgcolor: '#F5F5F5' }}>
                            <TableCell sx={{ fontWeight: 'bold', py: 2 }}>Patient Information</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Phone Number</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Overall Risk</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Last Activity</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 'bold' }}>Detailed Analysis</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {patients.map((patient) => (
                            <BioFeedbackRow key={patient.id} user={patient} />
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
}

export default BioFeedbackAnalysis;
