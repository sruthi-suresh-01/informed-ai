import React, { useState } from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, Button, TextField, Grid, Typography } from '@mui/material';

interface LoginDetails {
  email: string;
  password: string;
}

interface RegisterDetails {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface LoginDialogProps {
  open: boolean;
  onClose: () => void;
  onLogin: (details: LoginDetails) => void;
  onRegister: (details: RegisterDetails) => void;
}

const initialLoginDetails: LoginDetails = {
  email: '',
  password: ''
};

const initialRegisterDetails: RegisterDetails = {
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirmPassword: ''
};

export const LoginDialog: React.FC<LoginDialogProps> = ({ open, onClose, onLogin, onRegister }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [loginDetails, setLoginDetails] = useState<LoginDetails>(initialLoginDetails);
  const [registerDetails, setRegisterDetails] = useState<RegisterDetails>(initialRegisterDetails);

  const handleLoginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setLoginDetails((prev) => ({ ...prev, [name]: value }));
  };

  const handleRegisterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setRegisterDetails((prev) => ({ ...prev, [name]: value }));
  };

  const handleLogin = () => {
    onLogin(loginDetails);
    setLoginDetails(initialLoginDetails);
    onClose();
  };

  const handleRegister = () => {
    onRegister(registerDetails);
    setLoginDetails(initialLoginDetails);
    setRegisterDetails(initialRegisterDetails);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
      sx={{
        '.MuiDialogContent-root': {
          paddingTop: '20px !important',
        },
        '.MuiPaper-root': {
          maxHeight: '80vh',
        },
      }}
    >
      <DialogTitle>{isRegistering ? 'Register' : 'Login'}</DialogTitle>
      <DialogContent>
        {isRegistering ? (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="First Name"
                name="first_name"
                value={registerDetails.first_name}
                onChange={handleRegisterChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Last Name"
                name="last_name"
                value={registerDetails.last_name}
                onChange={handleRegisterChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Email"
                name="email"
                type="email"
                value={registerDetails.email}
                onChange={handleRegisterChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Password"
                name="password"
                type="password"
                value={registerDetails.password}
                onChange={handleRegisterChange}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Confirm Password"
                name="confirmPassword"
                type="password"
                value={registerDetails.confirmPassword}
                onChange={handleRegisterChange}
                fullWidth
              />
            </Grid>
          </Grid>
        ) : (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="Email"
                name="email"
                type="email"
                value={loginDetails.email}
                onChange={handleLoginChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Password"
                name="password"
                type="password"
                value={loginDetails.password}
                onChange={handleLoginChange}
                fullWidth
              />
            </Grid>
          </Grid>
        )}
        <Typography
          variant="body2"
          color="primary"
          onClick={() => setIsRegistering(!isRegistering)}
          sx={{ cursor: 'pointer', mt: 2 }}
        >
          {isRegistering ? 'Already have an account? Login' : "Don't have an account? Register"}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={isRegistering ? handleRegister : handleLogin} variant="contained">
          {isRegistering ? 'Register' : 'Login'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LoginDialog;
