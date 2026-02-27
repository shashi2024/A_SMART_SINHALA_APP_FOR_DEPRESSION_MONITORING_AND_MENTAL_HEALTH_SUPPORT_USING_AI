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
    Collapse,
    IconButton,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Dialog,
    DialogTitle,
    DialogContent,
    LinearProgress,
    Alert
} from '@mui/material';
import {
    CalendarToday,
    People,
    Description,
    Videocam,
    KeyboardArrowDown,
    KeyboardArrowUp,
} from '@mui/icons-material';
import CloseIcon from '@mui/icons-material/Close';
import TwitterIcon from '@mui/icons-material/Twitter';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

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
};

function TwitterAnalysisRow({ user, onRiskCalculated }) {
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const displayUsername = user.twitter_username || user.username;

    useEffect(() => {
        const fetchAnalysis = async () => {
            try {
                const cleanUsername = displayUsername ? displayUsername.replace('@', '') : '';
                if (!cleanUsername) {
                    setError("No Twitter username registered");
                    setLoading(false);
                    if (onRiskCalculated) onRiskCalculated(false); // No username means no depression found
                    return;
                }
                const response = await api.post('/twitter/predict', { username: cleanUsername });
                if (response.data.error) {
                    setError(response.data.error);
                    if (onRiskCalculated) onRiskCalculated(false);
                } else {
                    setResult(response.data);
                    const isHighRisk = parseFloat(response.data.depressed_percent) > 50;
                    if (onRiskCalculated) onRiskCalculated(isHighRisk);
                }
            } catch (err) {
                setError(err.response?.data?.detail || err.response?.data?.error || 'Failed to analyze Twitter profile.');
                if (onRiskCalculated) onRiskCalculated(false);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalysis();
    }, [displayUsername, onRiskCalculated]);

    const depressedPercent = result ? parseFloat(result.depressed_percent) : 0;
    const isHighRisk = depressedPercent > 50;

    return (
        <React.Fragment>
            <TableRow
                sx={{ '& > *': { borderBottom: 'unset' }, cursor: 'pointer', '&:hover': { bgcolor: '#F5F5F5' } }}
                onClick={() => setOpen(true)}
            >
                <TableCell>{user.username || 'N/A'}</TableCell>
                <TableCell>{user.email || 'N/A'}</TableCell>
                <TableCell>@{displayUsername?.replace('@', '')}</TableCell>
                <TableCell>
                    {loading ? <CircularProgress size={20} /> : error ? '0' : `${result.total_tweets}`}
                </TableCell>
                <TableCell>
                    {loading ? (
                        <CircularProgress size={20} />
                    ) : error ? (
                        <Chip label="Error" size="small" sx={{ bgcolor: '#eee', color: '#666', fontWeight: 600, borderRadius: 2 }} />
                    ) : (
                        <Chip
                            label={isHighRisk ? `High (${result.depressed_percent})` : `Low (${result.depressed_percent})`}
                            size="small"
                            sx={{
                                bgcolor: isHighRisk ? colors.red : colors.darkGreen,
                                color: 'white',
                                fontWeight: 600,
                                borderRadius: 2,
                            }}
                        />
                    )}
                </TableCell>
                <TableCell>
                    <IconButton aria-label="expand row" size="small" onClick={(e) => { e.stopPropagation(); setOpen(true); }}>
                        <KeyboardArrowDown />
                    </IconButton>
                </TableCell>
            </TableRow>

            {/* POPUP MODAL */}
            <Dialog
                open={open}
                onClose={() => setOpen(false)}
                PaperProps={{
                    sx: {
                        borderRadius: 4,
                        bgcolor: 'white',
                        minWidth: '400px',
                        maxWidth: '500px',
                        overflow: 'hidden'
                    }
                }}
            >
                <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TwitterIcon sx={{ color: '#1DA1F2' }} />
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>@{displayUsername?.replace('@', '')}</Typography>
                        {!loading && !error && result && (
                            <Chip
                                label={isHighRisk ? 'HIGH' : 'LOW'}
                                size="small"
                                sx={{
                                    bgcolor: isHighRisk ? colors.red : colors.darkGreen,
                                    color: 'white',
                                    fontWeight: 'bold',
                                    fontSize: '0.7rem',
                                    height: '20px',
                                    borderRadius: 1
                                }}
                            />
                        )}
                    </Box>
                    <IconButton onClick={() => setOpen(false)} size="small">
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>

                <DialogContent sx={{ p: 4, pt: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    {loading ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 5 }}>
                            <CircularProgress sx={{ mb: 2 }} />
                            <Typography color="text.secondary">Analyzing X timeline...</Typography>
                        </Box>
                    ) : error ? (
                        <Alert severity="error" sx={{ width: '100%' }}>{error}</Alert>
                    ) : result ? (
                        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            {/* Circular Risk Indicator */}
                            <Box sx={{ position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center', my: 2, width: 120, height: 120 }}>
                                <CircularProgress
                                    variant="determinate"
                                    value={100}
                                    size={100}
                                    thickness={6}
                                    sx={{ color: '#f0f0f0', position: 'absolute' }}
                                />
                                <CircularProgress
                                    variant="determinate"
                                    value={depressedPercent}
                                    size={100}
                                    thickness={6}
                                    sx={{
                                        color: isHighRisk ? colors.red : colors.darkGreen,
                                        strokeLinecap: 'round'
                                    }}
                                />
                                <Box sx={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                    <Typography variant="h5" sx={{ fontWeight: 'bold', color: isHighRisk ? colors.red : colors.darkGreen }}>
                                        {result.depressed_percent}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>risk</Typography>
                                </Box>
                            </Box>

                            {/* 3 Stats Boxes */}
                            <Grid container spacing={2} sx={{ mb: 4, width: '100%', mt: 1 }}>
                                <Grid item xs={4}>
                                    <Box sx={{ bgcolor: '#e3f2fd', p: 1.5, borderRadius: 3, textAlign: 'center' }}>
                                        <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#1976d2' }}>{result.total_tweets}</Typography>
                                        <Typography variant="caption" sx={{ color: '#555', fontWeight: 600 }}>Total</Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={4}>
                                    <Box sx={{ bgcolor: '#ffebee', p: 1.5, borderRadius: 3, textAlign: 'center' }}>
                                        <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#d32f2f' }}>{result.depressed_tweets || Math.round((depressedPercent / 100) * result.total_tweets)}</Typography>
                                        <Typography variant="caption" sx={{ color: '#555', fontWeight: 600 }}>Depressed</Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={4}>
                                    <Box sx={{ bgcolor: '#e8f5e9', p: 1.5, borderRadius: 3, textAlign: 'center' }}>
                                        <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#2e7d32' }}>{result.not_depressed_tweets || Math.round(((100 - depressedPercent) / 100) * result.total_tweets)}</Typography>
                                        <Typography variant="caption" sx={{ color: '#555', fontWeight: 600 }}>Healthy</Typography>
                                    </Box>
                                </Grid>
                            </Grid>

                            {/* Progress Bars */}
                            <Box sx={{ width: '100%', mb: 2 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                    <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: colors.red }} />
                                        Depressed Signals
                                    </Typography>
                                    <Typography variant="caption" sx={{ fontWeight: 'bold' }}>{result.depressed_percent}</Typography>
                                </Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={depressedPercent}
                                    sx={{ height: 8, borderRadius: 4, bgcolor: '#f5f5f5', '& .MuiLinearProgress-bar': { bgcolor: colors.red, borderRadius: 4 } }}
                                />
                            </Box>

                            <Box sx={{ width: '100%', mb: 3 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                    <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: colors.darkGreen }} />
                                        Healthy Signals
                                    </Typography>
                                    <Typography variant="caption" sx={{ fontWeight: 'bold' }}>{result.not_depressed_percent}</Typography>
                                </Box>
                                <LinearProgress
                                    variant="determinate"
                                    value={parseFloat(result.not_depressed_percent?.replace('%', '') || 0)}
                                    sx={{ height: 8, borderRadius: 4, bgcolor: '#f5f5f5', '& .MuiLinearProgress-bar': { bgcolor: colors.darkGreen, borderRadius: 4 } }}
                                />
                            </Box>

                            <Typography variant="caption" color="text.secondary">
                                Last Analyzed: {new Date().toLocaleDateString('en-CA')}
                            </Typography>
                        </Box>
                    ) : null}
                </DialogContent>
            </Dialog>
        </React.Fragment>
    );
}

function TwitterAnalysis() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [riskResults, setRiskResults] = useState({});

    const handleRiskCalculated = React.useCallback((userId, isHighRisk) => {
        setRiskResults(prev => ({
            ...prev,
            [userId]: isHighRisk
        }));
    }, []);

    const highRiskCount = Object.values(riskResults).filter(v => v === true).length;
    const lowRiskCount = Object.values(riskResults).filter(v => v === false).length;

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch normal users for the table
                const response = await api.get('/admin/users');
                const patients = response.data.users.filter(u => !u.is_admin && !u.is_sub_admin && u.role !== 'doctor' && u.role !== 'nurse');
                setUsers(patients);
            } catch (err) {
                console.error('Failed to fetch data:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const totalUsers = users.length;

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 4 }}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 4, display: 'flex', alignItems: 'center', gap: 1 }}>
                <TwitterIcon sx={{ color: '#1DA1F2', fontSize: 36 }} />
                Patient Twitter Analysis
            </Typography>

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={4}>
                    <Card sx={{ borderRadius: 3, bgcolor: colors.purple, color: 'white', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Box>
                                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>{totalUsers.toLocaleString()}</Typography>
                                    <Typography variant="body2" sx={{ opacity: 0.9 }}>Total Twitter Users</Typography>
                                </Box>
                                <CalendarToday sx={{ fontSize: 40, opacity: 0.8 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={4}>
                    <Card sx={{ borderRadius: 3, bgcolor: colors.red, color: 'white', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Box>
                                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>{highRiskCount}</Typography>
                                    <Typography variant="body2" sx={{ opacity: 0.9 }}>Depression Detected</Typography>
                                </Box>
                                <WarningIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={4}>
                    <Card sx={{ borderRadius: 3, bgcolor: colors.darkGreen, color: 'white', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Box>
                                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>{lowRiskCount}</Typography>
                                    <Typography variant="body2" sx={{ opacity: 0.9 }}>No Depression Detected</Typography>
                                </Box>
                                <CheckCircleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Patients Table */}
            <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                <Table>
                    <TableHead>
                        <TableRow sx={{ bgcolor: '#F5F5F5' }}>
                            <TableCell sx={{ fontWeight: 'bold' }}>Username</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Email</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Twitter Handle</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Tweets Analyzed</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Twitter Risk</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {users.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                                    <Typography variant="body2" sx={{ color: '#666' }}>No users found</Typography>
                                </TableCell>
                            </TableRow>
                        ) : (
                            users.map((user, index) => {
                                const uniqueId = user.user_id || user.id || user.username || `user-${index}`;
                                return (
                                    <TwitterAnalysisRow
                                        key={uniqueId}
                                        user={user}
                                        onRiskCalculated={(isHighRisk) => handleRiskCalculated(uniqueId, isHighRisk)}
                                    />
                                );
                            })
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
}

export default TwitterAnalysis;
