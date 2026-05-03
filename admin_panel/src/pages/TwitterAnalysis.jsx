// React core hooks
import React, { useState, useEffect } from 'react';

// API service (backend calls)
import api from '../services/api';

// Material UI components
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

// Material UI icons
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

/**
 * Color theme for dashboard UI
 */
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

/**
 * Each row = one user Twitter analysis
 */
function TwitterAnalysisRow({ user, onRiskCalculated }) {

    // row expand/collapse state (popup)
    const [open, setOpen] = useState(false);

    // loading state for API call
    const [loading, setLoading] = useState(true);

    // analysis result from backend
    const [result, setResult] = useState(null);

    // error handling state
    const [error, setError] = useState('');

    const displayUsername = user.twitter_username || user.username;

    /**
     * Fetch Twitter depression analysis when component loads
     */
    useEffect(() => {
        const fetchAnalysis = async () => {
            try {
                const cleanUsername = displayUsername
                    ? displayUsername.replace('@', '')
                    : '';

                // If no username available
                if (!cleanUsername) {
                    setError("No Twitter username registered");
                    setLoading(false);
                    if (onRiskCalculated) onRiskCalculated(false);
                    return;
                }

                // API call to backend prediction endpoint
                const response = await api.post('/twitter/predict', {
                    username: cleanUsername
                });

                // If backend returns error
                if (response.data.error) {
                    setError(response.data.error);
                    if (onRiskCalculated) onRiskCalculated(false);
                } else {
                    setResult(response.data);

                    // Convert percentage to number and check risk level
                    const isHighRisk = parseFloat(response.data.depressed_percent) > 50;

                    if (onRiskCalculated) onRiskCalculated(isHighRisk);
                }

            } catch (err) {
                // Handle API failure
                setError(
                    err.response?.data?.detail ||
                    err.response?.data?.error ||
                    'Failed to analyze Twitter profile.'
                );

                if (onRiskCalculated) onRiskCalculated(false);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalysis();
    }, [displayUsername, onRiskCalculated]);

    // Convert percentage string to number
    const depressedPercent = result ? parseFloat(result.depressed_percent) : 0;

    // High risk condition
    const isHighRisk = depressedPercent > 50;

    return (
        <>
            {/* Table Row UI */}
            <TableRow
                sx={{
                    cursor: 'pointer',
                    '&:hover': { bgcolor: '#F5F5F5' }
                }}
                onClick={() => setOpen(true)}
            >

                <TableCell>{user.username || 'N/A'}</TableCell>
                <TableCell>{user.email || 'N/A'}</TableCell>
                <TableCell>@{displayUsername?.replace('@', '')}</TableCell>

                {/* Tweet count */}
                <TableCell>
                    {loading ? (
                        <CircularProgress size={20} />
                    ) : error ? (
                        '0'
                    ) : (
                        `${result.total_tweets}`
                    )}
                </TableCell>

                {/* Risk indicator */}
                <TableCell>
                    {loading ? (
                        <CircularProgress size={20} />
                    ) : error ? (
                        <Chip label="Error" size="small" />
                    ) : (
                        <Chip
                            label={
                                isHighRisk
                                    ? `High (${result.depressed_percent})`
                                    : `Low (${result.depressed_percent})`
                            }
                            size="small"
                            sx={{
                                bgcolor: isHighRisk ? colors.red : colors.darkGreen,
                                color: 'white'
                            }}
                        />
                    )}
                </TableCell>

                {/* expand button */}
                <TableCell>
                    <IconButton
                        onClick={(e) => {
                            e.stopPropagation();
                            setOpen(true);
                        }}
                    >
                        <KeyboardArrowDown />
                    </IconButton>
                </TableCell>
            </TableRow>

            {/* POPUP DIALOG - detailed analysis view */}
            <Dialog open={open} onClose={() => setOpen(false)}>

                <DialogTitle>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography>@{displayUsername?.replace('@', '')}</Typography>
                        <IconButton onClick={() => setOpen(false)}>
                            <CloseIcon />
                        </IconButton>
                    </Box>
                </DialogTitle>

                <DialogContent>

                    {/* Loading state */}
                    {loading ? (
                        <CircularProgress />
                    ) : error ? (
                        <Alert severity="error">{error}</Alert>
                    ) : result ? (
                        <>
                            {/* Risk percentage display */}
                            <Typography>
                                Risk: {result.depressed_percent}
                            </Typography>

                            {/* Tweet statistics */}
                            <Typography>Total Tweets: {result.total_tweets}</Typography>
                            <Typography>Depressed: {result.depressed_tweets}</Typography>
                            <Typography>Healthy: {result.not_depressed_tweets}</Typography>
                        </>
                    ) : null}

                </DialogContent>
            </Dialog>
        </>
    );
}

/**
 * Main dashboard component
 * - Loads all users
 * - Shows Twitter risk analysis table
 */
function TwitterAnalysis() {

    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    // store risk results per user
    const [riskResults, setRiskResults] = useState({});

    /**
     * Store risk per user (high/low)
     */
    const handleRiskCalculated = React.useCallback((userId, isHighRisk) => {
        setRiskResults(prev => ({
            ...prev,
            [userId]: isHighRisk
        }));
    }, []);

    // Count high risk users
    const highRiskCount = Object.values(riskResults).filter(v => v === true).length;

    // Count low risk users
    const lowRiskCount = Object.values(riskResults).filter(v => v === false).length;

    /**
     * Load users from backend
     */
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('/admin/users');

                // filter only patients (not doctors/admins)
                const patients = response.data.users.filter(u =>
                    !u.is_admin &&
                    !u.is_sub_admin &&
                    u.role !== 'doctor' &&
                    u.role !== 'nurse'
                );

                setUsers(patients);

            } catch (err) {
                console.error('Failed to fetch data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return <CircularProgress />;
    }

    return (
        <Box sx={{ p: 4 }}>

            {/* Header */}
            <Typography variant="h4">
                Twitter Analysis Dashboard
            </Typography>

            {/* Table */}
            <TableContainer component={Paper}>
                <Table>

                    <TableHead>
                        <TableRow>
                            <TableCell>Username</TableCell>
                            <TableCell>Email</TableCell>
                            <TableCell>Twitter</TableCell>
                            <TableCell>Tweets</TableCell>
                            <TableCell>Risk</TableCell>
                            <TableCell>Action</TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {users.map((user, index) => {
                            const id = user.user_id || user.id || index;

                            return (
                                <TwitterAnalysisRow
                                    key={id}
                                    user={user}
                                    onRiskCalculated={(isHighRisk) =>
                                        handleRiskCalculated(id, isHighRisk)
                                    }
                                />
                            );
                        })}
                    </TableBody>

                </Table>
            </TableContainer>

        </Box>
    );
}

export default TwitterAnalysis;
