import React, { useState } from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, Button, TextField, Grid, Typography } from '@mui/material';

const LoginDialog = ({ open, onClose, onLogin, onRegister }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [loginDetails, setLoginDetails] = useState({ email: '', password: '' });
  const [registerDetails, setRegisterDetails] = useState({ first_name: '', last_name: '', email: '', password: '', confirmPassword: '' });

  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginDetails((prevDetails) => ({ ...prevDetails, [name]: value }));
  };

  const handleRegisterChange = (e) => {
    const { name, value } = e.target;
    setRegisterDetails((prevDetails) => ({ ...prevDetails, [name]: value }));
  };

  const handleLogin = () => {
    onLogin(loginDetails);
    setLoginDetails({ email: '', password: '' })
    onClose();
  };

  const handleRegister = () => {
    onRegister(registerDetails);
    setLoginDetails({ email: '', password: '' })
    setRegisterDetails({ first_name: '', last_name: '', email: '', password: '', confirmPassword: '' })
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm"
    sx={{
        '.MuiDialogContent-root': {
        paddingTop: '20px !important',
        },
        '.MuiPaper-root': {
          maxHeight: '80vh', // Set your desired max height here
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
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Last Name"
                name="last_name"
                value={registerDetails.last_name}
                onChange={handleRegisterChange}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Email"
                name="email"
                value={registerDetails.email}
                onChange={handleRegisterChange}
                fullWidth
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
                value={loginDetails.email}
                onChange={handleLoginChange}
                fullWidth
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
        <Button onClick={onClose} color="primary">
          Cancel
        </Button>
        <Button onClick={isRegistering ? handleRegister : handleLogin} color="primary">
          {isRegistering ? 'Register' : 'Login'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LoginDialog;
