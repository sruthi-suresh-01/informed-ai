// import React, { useState } from 'react';
// import { Dialog, DialogActions, DialogContent, DialogTitle, Button, TextField, Grid, Typography } from '@mui/material';

// const LoginComponent = ({ open, onClose, onLogin, onRegister }) => {
//   const [isRegistering, setIsRegistering] = useState(false);
//   const [loginDetails, setLoginDetails] = useState({ username: '', password: '' });
//   const [registerDetails, setRegisterDetails] = useState({ username: '', email: '', password: '', confirmPassword: '' });

//   const handleLoginChange = (e) => {
//     const { name, value } = e.target;
//     setLoginDetails((prevDetails) => ({ ...prevDetails, [name]: value }));
//   };

//   const handleRegisterChange = (e) => {
//     const { name, value } = e.target;
//     setRegisterDetails((prevDetails) => ({ ...prevDetails, [name]: value }));
//   };

//   const handleLogin = () => {
//     onLogin(loginDetails);
//     onClose();
//   };

//   const handleRegister = () => {
//     onRegister(registerDetails);
//     onClose();
//   };

//   return (
//     <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm"
//     sx={{
//         '.MuiDialogContent-root': {
//         paddingTop: '20px !important',
//         },
//         '.MuiPaper-root': {
//           maxHeight: '80vh', // Set your desired max height here
//         },
        
//     }}
//     >
//       <DialogTitle>{isRegistering ? 'Register' : 'Login'}</DialogTitle>
//       <DialogContent>
//         {isRegistering ? (
//           <Grid container spacing={2}>
//             <Grid item xs={12}>
//               <TextField
//                 label="Username"
//                 name="username"
//                 value={registerDetails.username}
//                 onChange={handleRegisterChange}
//                 fullWidth
//               />
//             </Grid>
//             <Grid item xs={12}>
//               <TextField
//                 label="Email"
//                 name="email"
//                 value={registerDetails.email}
//                 onChange={handleRegisterChange}
//                 fullWidth
//               />
//             </Grid>
//             <Grid item xs={12}>
//               <TextField
//                 label="Password"
//                 name="password"
//                 type="password"
//                 value={registerDetails.password}
//                 onChange={handleRegisterChange}
//                 fullWidth
//               />
//             </Grid>
//             <Grid item xs={12}>
//               <TextField
//                 label="Confirm Password"
//                 name="confirmPassword"
//                 type="password"
//                 value={registerDetails.confirmPassword}
//                 onChange={handleRegisterChange}
//                 fullWidth
//               />
//             </Grid>
//           </Grid>
//         ) : (
//           <Grid container spacing={2}>
//             <Grid item xs={12}>
//               <TextField
//                 label="Username"
//                 name="username"
//                 value={loginDetails.username}
//                 onChange={handleLoginChange}
//                 fullWidth
//               />
//             </Grid>
//             <Grid item xs={12}>
//               <TextField
//                 label="Password"
//                 name="password"
//                 type="password"
//                 value={loginDetails.password}
//                 onChange={handleLoginChange}
//                 fullWidth
//               />
//             </Grid>
//           </Grid>
//         )}
//         <Typography
//           variant="body2"
//           color="primary"
//           onClick={() => setIsRegistering(!isRegistering)}
//           sx={{ cursor: 'pointer', mt: 2 }}
//         >
//           {isRegistering ? 'Already have an account? Login' : "Don't have an account? Register"}
//         </Typography>
//       </DialogContent>
//       <DialogActions>
//         <Button onClick={onClose} color="primary">
//           Cancel
//         </Button>
//         <Button onClick={isRegistering ? handleRegister : handleLogin} color="primary">
//           {isRegistering ? 'Register' : 'Login'}
//         </Button>
//       </DialogActions>
//     </Dialog>
//   );
// };

// export default LoginComponent;
