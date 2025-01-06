import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { IconButton, Menu, MenuItem, Avatar } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import * as userActions from '../../store/actionCreators/userActionCreators';
import { RootState } from '../../store/types';
import { AppDispatch } from '../../store/store';
import LoginDialog from './LoginDialog';
import styles from './UserMenu.module.css';

interface UserDetails {
  first_name?: string;
  last_name?: string;
}

interface User {
  account_type?: 'admin' | 'superadmin' | 'user';
  details?: UserDetails;
}

export const UserMenu: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const user = useSelector((state: RootState) => state.user.user as User);
  const isLoggedIn = useSelector((state: RootState) => state.user.loggedIn);
  const isAdmin = user?.account_type === 'admin' || user?.account_type === 'superadmin';

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleMenuClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleOpenDialog = () => {
    setIsDialogOpen(true);
    handleMenuClose();
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
  };

  const handleLogin = (loginDetails: { email: string; password: string }) => {
    dispatch(userActions.login({ ...loginDetails }));
  };

  const handleRegister = (registerDetails: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    confirmPassword: string;
  }) => {
    dispatch(userActions.registerUser({ ...registerDetails }));
  };

  const handleLogout = () => {
    dispatch(userActions.logout());
    handleMenuClose();
    navigate('/');
  };

  const handleAdminClick = () => {
    navigate('/admin');
    handleMenuClose();
  };

  return (
    <div className={styles.AuthComponent}>
      <div className={styles.menuContainer}>
        <IconButton onClick={handleMenuClick} size="large" className={styles.accountIcon}>
          {isLoggedIn ? (
            <Avatar className={styles.avatar}>
              {user?.details?.first_name?.[0]}{user?.details?.last_name?.[0]}
            </Avatar>
          ) : (
            <AccountCircleIcon />
          )}
        </IconButton>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          slotProps={{
            paper: {
              sx: {
                minWidth: '200px',
                mt: 1.5,
                '& .MuiMenuItem-root': {
                  padding: '8px 16px'
                }
              }
            }
          }}
        >
          {isLoggedIn ? [
            <MenuItem key="name" disabled>
              {user?.details?.first_name} {user?.details?.last_name}
            </MenuItem>,
            isAdmin && (
              <MenuItem key="admin" onClick={handleAdminClick}>Admin Panel</MenuItem>
            ),
            <MenuItem key="logout" onClick={handleLogout}>Logout</MenuItem>
          ].filter(Boolean) : (
            <MenuItem onClick={handleOpenDialog}>Login</MenuItem>
          )}
        </Menu>
      </div>

      <LoginDialog
        open={isDialogOpen}
        onClose={handleCloseDialog}
        onLogin={handleLogin}
        onRegister={handleRegister}
      />
    </div>
  );
};

export default UserMenu;
