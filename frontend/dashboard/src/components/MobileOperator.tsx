import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  BottomNavigation,
  BottomNavigationAction,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Fab,
  Badge
} from '@mui/material';
import {
  Menu as MenuIcon,
  LocalShipping,
  Inventory,
  Assignment,
  CameraAlt,
  Notifications
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export const MobileOperator: React.FC = () => {
  const { user } = useAuth();
  const [value, setValue] = useState(0);
  const [notifications] = useState(3);

  const tasks = [
    { id: 1, title: 'Заполнить бункер', location: 'Машина #1', urgent: true },
    { id: 2, title: 'Чистка машины', location: 'Машина #5', urgent: false },
    { id: 3, title: 'Проверка температуры', location: 'Машина #3', urgent: false }
  ];

  return (
    <Box sx={{ pb: 7, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            VendBot
          </Typography>
          <IconButton color="inherit">
            <Badge badgeContent={notifications} color="error">
              <Notifications />
            </Badge>
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Привет, {user?.full_name || user?.username}! 👋
        </Typography>
        
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Ваши задачи на сегодня:
        </Typography>

        <List>
          {tasks.map((task) => (
            <Paper key={task.id} sx={{ mb: 1 }}>
              <ListItem>
                <ListItemIcon>
                  <Assignment color={task.urgent ? "error" : "primary"} />
                </ListItemIcon>
                <ListItemText
                  primary={task.title}
                  secondary={task.location}
                  primaryTypographyProps={{
                    fontWeight: task.urgent ? 'bold' : 'normal'
                  }}
                />
              </ListItem>
            </Paper>
          ))}
        </List>
      </Box>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="camera"
        sx={{
          position: 'fixed',
          bottom: 80,
          right: 16,
        }}
      >
        <CameraAlt />
      </Fab>

      {/* Bottom Navigation */}
      <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
        <BottomNavigation
          value={value}
          onChange={(event, newValue) => {
            setValue(newValue);
          }}
        >
          <BottomNavigationAction label="Задачи" icon={<Assignment />} />
          <BottomNavigationAction label="Бункера" icon={<Inventory />} />
          <BottomNavigationAction label="Маршрут" icon={<LocalShipping />} />
        </BottomNavigation>
      </Paper>
    </Box>
  );
};