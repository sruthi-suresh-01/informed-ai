import React, { useState } from 'react';
import styles from './LoginModal.module.css';
const LoginModal = ({ onClose, onLogin }) => {
  const [email, setEmail] = useState('');

  const handleLogin = () => {
    onLogin(email);
    setEmail('');
    onClose();
  };

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
  const [email, setEmail] = useState('');

  const handleLogin = (email) => {
    setEmail(email);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setEmail('');
    setIsLoggedIn(false);
  };

  return (
    <div>
      {isLoggedIn ? (
        <div>
          <span>Welcome, {email}!</span>
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
