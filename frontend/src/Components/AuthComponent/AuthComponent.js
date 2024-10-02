import React, { useState, useEffect } from 'react';
import styles from './LoginModal.module.css';
import { useDispatch, useSelector } from 'react-redux';
import * as userActions from '../../store/actionCreators/userActionCreators'
import LoginDialog from './LoginDialog';
import DialogWrapper from '../DialogWrapper/DialogWrapper';



const AuthComponent = () => {
  const dispatch = useDispatch();
  const user = useSelector(state => state.user.user)
  const isLoggedIn = useSelector(state => state.user.loggedIn)

  const displayName = (user && user.details && user.details.first_name && user.details.last_name &&  `${user.details.first_name} ${user.details.last_name}`) || ''

  const [isRegistering, setIsRegistering] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleOpenDialog = () => {
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
  };

  const handleLogin = (loginDetails) => {
    dispatch(userActions.login({ ...loginDetails }))
  };

  const handleRegister = (registerDetails) => {
    dispatch(userActions.registerUser({ ...registerDetails }))
  };

  const handleLogout = () => {
    dispatch(userActions.logout())
  };

  return (
    <div className={styles.AuthComponent}>
        <div className={styles.loginlogoutContainer}>
            {isLoggedIn ? (
            <button className={styles.close} onClick={handleLogout}>Logout</button>
            ) : (
                <button className={styles.loginButton} onClick={handleOpenDialog}>Login</button>
            )}
        </div>

        {
        isLoggedIn &&
            <div className={styles.loggedInMsg}><p>Welcome, {displayName}!</p></div>
        }

      <LoginDialog
        open={isDialogOpen}
        onClose={handleCloseDialog}
        onLogin={handleLogin}
        onRegister={handleRegister}
      />
    </div>
  );
};


export default AuthComponent;
