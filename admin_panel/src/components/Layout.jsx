import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
  InputAdornment,
  Avatar,
  Typography,
  IconButton,
  Badge,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BarChartIcon from '@mui/icons-material/BarChart';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import ShoppingBagIcon from '@mui/icons-material/ShoppingBag';
import TimelineIcon from '@mui/icons-material/Timeline';
import ChatBubbleIcon from '@mui/icons-material/ChatBubble';
import SettingsIcon from '@mui/icons-material/Settings';
import PeopleIcon from '@mui/icons-material/People';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import TwitterIcon from '@mui/icons-material/Twitter';
import SearchIcon from '@mui/icons-material/Search';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import FolderIcon from '@mui/icons-material/Folder';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const drawerWidth = 280;

// Color palette
const colors = {
  darkGreen: '#185846',
  paleSageGreen: '#D2DEBF',
  lightPeach: '#ECD0B6',
  creamYellow: '#F2E8C9',
  veryLightBlue: '#E5F1F5',
  lightPink: '#FFF5F5',
};

function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user, checkAdminStatus } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  
  // Fetch user info on mount
  useEffect(() => {
    if (!user) {
      checkAdminStatus();
    }
  }, []);

  // Fetch notification count
  const fetchNotificationCount = async () => {
    try {
      const response = await api.get('/admin/notifications');
      const notifications = response.data.notifications || [];
      const unread = notifications.filter(n => !n.is_read).length;
      setUnreadCount(unread);
    } catch (error) {
      console.error('Failed to fetch notification count:', error);
    }
  };

  useEffect(() => {
    // Fetch immediately and then every 15 seconds
    fetchNotificationCount();
    const interval = setInterval(fetchNotificationCount, 15000);

    return () => clearInterval(interval);
  }, [user]);
  
  // Refresh when navigating to/from notifications page
  useEffect(() => {
    if (location.pathname === '/notifications' || location.pathname === '/connect') {
      fetchNotificationCount();
    }
  }, [location.pathname]);
  const displayName = user?.username || user?.email?.split('@')[0] || 'Admin';

  // Build menu items based on user role
  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Patients Risk Level', icon: <BarChartIcon />, path: '/patients-risk' },
    { text: 'Alerts Management', icon: <CalendarTodayIcon />, path: '/alerts' },
    { text: 'Doctor Connect', icon: <ShoppingBagIcon />, path: '/connect' },
    { text: 'Location track', icon: <TimelineIcon />, path: '/location-track' },
    { text: 'Digital twin', icon: <ChatBubbleIcon />, path: '/digital-twin' },
    { text: 'X (Twitter) Analysis', icon: <TwitterIcon />, path: '/twitter-analysis' },

    // Only show User Management for full admins (not sub-admins, doctors, or nurses)
    ...(user?.is_admin ? [{ text: 'User Management', icon: <PeopleIcon />, path: '/user-management' }] : []),
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/';
    }
    return location.pathname === path;
  };

  return (
    <Box sx={{ display: 'flex', bgcolor: colors.lightPink, minHeight: '100vh' }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: '#F5F5F5',
            borderRight: 'none',
          },
        }}
      >
        {/* Logo */}
        <Box
          sx={{
            p: 3,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            bgcolor: colors.lightPink,
          }}
        >
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '50%',
              bgcolor: colors.lightPink,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
            }}
          >
            {/* Logo icon - simplified brain/heart design */}
            <Box
              sx={{
                width: 30,
                height: 30,
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
                  width: 20,
                  height: 20,
                  borderRadius: '50%',
                  bgcolor: colors.darkGreen,
                  position: 'absolute',
                  top: -2,
                  right: -2,
                }}
              />
            </Box>
          </Box>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 'bold',
              color: colors.darkGreen,
              fontSize: '18px',
            }}
          >
            Dashboard
          </Typography>
        </Box>

        {/* Menu Items */}
        <List sx={{ px: 2, pt: 2 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={isActive(item.path)}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  bgcolor: isActive(item.path) ? colors.darkGreen : 'transparent',
                  color: isActive(item.path) ? 'white' : '#666',
                  '&:hover': {
                    bgcolor: isActive(item.path) ? colors.darkGreen : 'rgba(0,0,0,0.04)',
                  },
                  '&.Mui-selected': {
                    bgcolor: colors.darkGreen,
                    color: 'white',
                    '&:hover': {
                      bgcolor: colors.darkGreen,
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive(item.path) ? 'white' : '#666',
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '14px',
                    fontWeight: isActive(item.path) ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        {/* Sign Out */}
        <Box sx={{ px: 2, mt: 'auto', mb: 2 }}>
          <ListItem disablePadding>
            <ListItemButton
              onClick={handleLogout}
              sx={{
                borderRadius: 2,
                color: '#666',
                '&:hover': {
                  bgcolor: 'rgba(0,0,0,0.04)',
                },
              }}
            >
              <ListItemIcon sx={{ color: '#666', minWidth: 40 }}>
                <ExitToAppIcon />
              </ListItemIcon>
              <ListItemText
                primary="Sign Out"
                primaryTypographyProps={{ fontSize: '14px' }}
              />
            </ListItemButton>
          </ListItem>
        </Box>
      </Drawer>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: colors.lightPink,
          minHeight: '100vh',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            bgcolor: 'white',
            px: 4,
            py: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
          }}
        >
          {/* Search Bar */}
          <TextField
            placeholder="Search here..."
            size="small"
            sx={{
              width: 300,
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                bgcolor: '#F5F5F5',
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: '#999' }} />
                </InputAdornment>
              ),
            }}
          />

          {/* Right Side - Welcome Message and Profile */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            {/* Welcome Message */}
            <Box sx={{ textAlign: 'right' }}>
              <Typography
                variant="body1"
                sx={{ fontWeight: 600, color: '#333', fontSize: '16px' }}
              >
                Welcome, {displayName}
              </Typography>
              <Typography
                variant="body2"
                sx={{ color: '#999', fontSize: '12px' }}
              >
                Have a nice day at great work
              </Typography>
            </Box>

            {/* Top Navigation Icons */}
            <IconButton
              sx={{ color: '#666' }}
              onClick={() => navigate('/notifications')}
              title="Notifications"
            >
              <Badge badgeContent={unreadCount} color="error">
                <NotificationsNoneIcon />
              </Badge>
            </IconButton>
            <IconButton
              sx={{ color: '#666' }}
              onClick={() => navigate('/reports')}
              title="Reports"
            >
              <FolderIcon />
            </IconButton>

            {/* Profile */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                cursor: 'pointer',
                px: 2,
                py: 1,
                borderRadius: 2,
                '&:hover': {
                  bgcolor: '#F5F5F5',
                },
              }}
              onClick={() => navigate('/admin-profile')}
            >
              <Avatar
                sx={{
                  width: 40,
                  height: 40,
                  bgcolor: colors.darkGreen,
                }}
              >
                {displayName.charAt(0).toUpperCase()}
              </Avatar>
              <Box>
                <Typography
                  variant="body2"
                  sx={{ fontWeight: 600, color: '#333', fontSize: '14px' }}
                >
                  {displayName}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ color: '#999', fontSize: '12px' }}
                >
                  {user?.is_admin ? 'Administrator' : 'User'}
                </Typography>
              </Box>
              <Typography sx={{ color: '#999', ml: 0.5 }}>▼</Typography>
            </Box>
          </Box>
        </Box>

        {/* Page Content */}
        <Box sx={{ p: 0 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}

export default Layout;
