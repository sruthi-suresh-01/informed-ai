import React, { useState, useEffect } from 'react';
import styles from './LoginModal.module.css';
import { useDispatch, useSelector } from 'react-redux';
import * as userActions from '../../store/actionCreators/userActionCreators'
const LoginModal = ({ onClose, onLogin }) => {

  const dispatch = useDispatch();
  const user = useSelector(state => state.user.user);
  const error = useSelector(state => state.user.error);
  const isLoading = useSelector(state => state.user.isLoading);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    dispatch(userActions.login({ username }))
    // onLogin(username);
    setUsername('');
    setPassword('')
    // onClose();
  };

  useEffect(() => {
    // console.info(`Waiting for response: ${waitingForResponse}`);
    if(user && user.username) {
      onLogin(user.username);
      onClose();
    }
    
    return () => {
        // clearInterval(intervalID)
    };
}, [user]);

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
            
        <div className={styles.loginModalHeading}>
            <p>Enter User Details</p>
            <div className={styles.closeButtonContainer} onClick={onClose}>
                x
            </div>
        </div>
        
        <div className={styles.loginActionsContainer}>
          <div className={styles.loginFormContainer}>
            <div className={styles.userNameInputContainer}>
                <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={styles.userNameInput}
                />
            </div>
            <div className={styles.passwordInputContainer}>
                <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={styles.userNameInput}
                />
            </div>
          </div>
            <div className={styles.usernameSubmitContainer}>
                <button className={styles.usernameSubmit} onClick={handleLogin}>Login</button>
            </div>
            
        </div>
        
      </div>
    </div>
  );
};

const AuthComponent = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [username, setUsername] = useState('');

  const handleLogin = (username) => {
    setUsername(username);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setUsername('');
    setIsLoggedIn(false);
  };

  return (
    <div className={styles.AuthComponent}>
        <div className={styles.loginlogoutContainer}>
            {isLoggedIn ? (
            <button className={styles.close} onClick={handleLogout}>Logout</button>
            ) : (
                <button onClick={() => setShowModal(true)}>Login</button>
            )}
        </div>
    
        {
        isLoggedIn &&
            <div className={styles.loggedInMsg}>Welcome, {username}!</div>
        }

        {showModal && (
        <LoginModal
            onClose={() => setShowModal(false)}
            onLogin={handleLogin}
        />
        )}
    </div>
  );
};

export default AuthComponent;
