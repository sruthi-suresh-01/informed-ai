import React, { useState } from 'react';
import styles from './LoginModal.module.css';
const LoginModal = ({ onClose, onLogin }) => {
  const [username, setUsername] = useState('');

  const handleLogin = () => {
    onLogin(username);
    setUsername('');
    onClose();
  };

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Enter your username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button onClick={handleLogin}>Login</button>
        <button onClick={onClose}>Cancel</button>
      </div>
    </div>
  );
};

const LogoutButton = ({ onLogout }) => (
  <button className={styles.close} onClick={onLogout}>Logout</button>
);

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
    <div>
      {isLoggedIn ? (
        <div>
          <span>Welcome, {username}!</span>
          <LogoutButton onLogout={handleLogout} />
        </div>
      ) : (
        <button onClick={() => setShowModal(true)}>Login</button>
      )}

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
